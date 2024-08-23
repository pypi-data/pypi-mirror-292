import prettytable
from typing import List, Dict, Optional
import click
import sys
import os
import opus
import jinja2
import pendulum
from contextlib import contextmanager
import paramiko
from paramiko.config import SSHConfig
from opus import opus_logging
import subprocess
from opus.clouds import Slurm
import socket
from contextlib import closing
import getpass
import re

logger = opus_logging.init_logger(__name__)

def create_table(field_names: List[str], **kwargs) -> prettytable.PrettyTable:
    """Creates table with default style."""
    border = kwargs.pop('border', False)
    align = kwargs.pop('align', 'l')
    table = prettytable.PrettyTable(align=align,
                                    border=border,
                                    field_names=field_names,
                                    **kwargs)
    table.left_padding_width = 0
    table.right_padding_width = 2
    return table

def check_accelerators_format(accelerators: str) -> bool:
    parts = accelerators.split(":")
    if len(parts) != 2 or parts[0] == "" or parts[1] == "":
        click.secho("Invalid accelerators format. It should be formatted as 'str:str', e.g. NVIDIA-A100:1", 
                    fg='red', nl=True)
        sys.exit(1)
    else:
        return True
    
def fill_template(template_name: str, variables: Dict,
                  output_path: str) -> None:
    """Create a file from a Jinja template."""
    template_path = os.path.join(opus.__root_dir__, 'templates', template_name)
    if not os.path.exists(template_path):
        raise FileNotFoundError(f'Template "{template_name}" does not exist.')
    with open(template_path) as fin:
        template = fin.read()
    output_path = os.path.abspath(os.path.expanduser(output_path))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write out config.
    j2_template = jinja2.Template(template)
    content = j2_template.render(**variables)
    with open(output_path, 'w') as fout:
        fout.write(content)

def format_shell_cmds(cmd: str) -> str:
    return ' && '.join(cmd.rstrip('\n').split('\n'))

def readable_time_duration(start: Optional[float],
                           end: Optional[float] = None,
                           absolute: bool = False) -> str:
    """Human readable time duration from timestamps.

    Args:
        start: Start timestamp.
        end: End timestamp. If None, current time is used.
        absolute: Whether to return accurate time duration.
    Returns:
        Human readable time duration. e.g. "1 hour ago", "2 minutes ago", etc.
        If absolute is specified, returns the accurate time duration,
          e.g. "1h 2m 23s"
    """
    # start < 0 means that the starting time is not specified yet.
    if start is None or start < 0:
        return '-'
    if end == start == 0:
        return '-'
    if end is not None:
        end = pendulum.from_timestamp(end)
    start_time = pendulum.from_timestamp(start)
    duration = start_time.diff(end)
    if absolute:
        diff = start_time.diff(end).in_words()
        if duration.in_seconds() < 1:
            diff = '< 1 second'
        diff = diff.replace(' seconds', 's')
        diff = diff.replace(' second', 's')
        diff = diff.replace(' minutes', 'm')
        diff = diff.replace(' minute', 'm')
        diff = diff.replace(' hours', 'h')
        diff = diff.replace(' hour', 'h')
        diff = diff.replace(' days', 'd')
        diff = diff.replace(' day', 'd')
        diff = diff.replace(' weeks', 'w')
        diff = diff.replace(' week', 'w')
        diff = diff.replace(' months', 'mo')
        diff = diff.replace(' month', 'mo')
    else:
        diff = start_time.diff_for_humans(end)
        if duration.in_seconds() < 1:
            diff = '< 1 second'
        diff = diff.replace('second', 'sec')
        diff = diff.replace('minute', 'min')
        diff = diff.replace('hour', 'hr')

    return diff

@contextmanager
def ssh_client(hostname: str, username: Optional[str] = None, password: Optional[str] = None):
    """Context manager for creating an SSH client connection."""
    config_file = os.path.expanduser('~/.ssh/config')
    host_config = {}
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    if os.path.isfile(config_file):
        config = SSHConfig.from_file(open(config_file))
        host_config = config.lookup(hostname)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=hostname, key_filename=host_config.get('identityfile'), username=username, password=password)
        yield ssh
    except Exception as e:
        raise e
    finally:
        ssh.close()
    
def get_rsync_command(source: str, destination: str, remote_host: Optional[str], upload: bool = True, ssh_key: Optional[str] = None) -> str:
    """Generate rsync command."""
    rsync_command = "rsync -avz"
    if remote_host:
        rsync_command += " -e ssh"
        if ssh_key:
            rsync_command += f" -i {ssh_key}"
        remote_host = f'{remote_host}:'
    else:
        remote_host = ''

    if upload:
        rsync_command += f" {source} {remote_host}{destination}"
    else:
        rsync_command += f" {remote_host}{source} {destination}"
    return rsync_command

def rsync(source: str, destination: str, remote_host: Optional[str], upload: bool = True, ssh_key: Optional[str] = None) -> None:
    """Sync file between local and remote host"""
    execute_command(get_rsync_command(source, destination, remote_host, upload, ssh_key))

def rsync_through_slurm(source: str, 
                        destination: str, 
                        remote_host: Optional[str], 
                        partition: str, 
                        upload: bool = True, 
                        ssh_key: Optional[str] = None):
    """Execute rsync through slurm srun."""
    Slurm.launch_srun_job(get_rsync_command(source, destination, remote_host, upload, ssh_key), 
                          partition, cpus_per_task=4, nodes_num=1)

def execute_command(command: str, 
                    remote_host: Optional[str] = None, 
                    input: Optional[str]=None,
                    timeout: Optional[str]=None) -> str:
    """Execute the command on a specific host."""
    try:
        if remote_host is None:
            process_output = subprocess.run(command, input=input, timeout=timeout, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = process_output.stdout.decode('utf-8')
        else:
            with ssh_client(remote_host) as ssh:
                _, process_output, stderr = ssh.exec_command(command, timeout=timeout)
                stderr_output = stderr.read().decode('utf-8')
                if stderr_output:
                    raise Exception(stderr_output)
                output = process_output.read().decode('utf-8')
    except Exception as e:
        raise e
    return output

def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
    
def get_current_user():
    try:
        return getpass.getuser()
    except Exception as e:
        logger.warn(f"Failed to get the current user: {e}")
        return None
    
def rfc1035_compliant(input_str: str) -> str:
    """
    Convert a given string into a format compliant with RFC 1035.  
    - contain at most 63 characters
    - contain only lowercase alphanumeric characters or '-'
    - start with an alphabetic character
    - end with an alphanumeric character
    """
    input_str = input_str.lower()
    input_str = re.sub(r'[^a-z0-9-]', '', input_str)
    input_str = input_str[:63]

    if input_str and not input_str[0].isalpha():
        input_str = 'a' + input_str[1:]

    if input_str and not input_str[-1].isalnum():
        input_str = input_str[:-1] + 'a'
    
    return input_str

def convert_to_ordinal(num: int) -> str:
    if num % 10 == 1 and num % 100 != 11:
        suffix = "st"
    elif num % 10 == 2 and num % 100 != 12:
        suffix = "nd"
    elif num % 10 == 3 and num % 100 != 13:
        suffix = "rd"
    else:
        suffix = "th"
    return str(num) + suffix

def is_port_open(port):
    """Check if the port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0