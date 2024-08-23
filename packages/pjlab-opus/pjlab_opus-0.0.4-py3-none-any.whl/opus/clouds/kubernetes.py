from opus.clouds import cloud
from typing import Tuple, Optional, List, Type
from opus import opus_logging
from opus.common_types import CloudJobInfo, RayLaunchParams, RayClusterDetails
from opus.utils import common_utils
from kubernetes import config, dynamic, client
from kubernetes.dynamic.exceptions import ResourceNotFoundError, NotFoundError
from kubernetes.client.rest import ApiException
import os
import click
import json
import yaml
import urllib3
import sys
import colorama
import subprocess
import signal
import time
import atexit
from urllib import parse
import base64

RAY_TEMPLATE = 'kubernetes-ray-template.yaml.j2'
# Store the YAML file defined by each generated Ray cluster.
RAY_CLUSTER_YAML_PREFIX = '~/opus/kubernetes_ray_cluster_yaml'
# TODO: replace image
RAY_IMAGE = 'redpanda123321/pj-ray-llm:2.3.1-py310-cu118'

logger = opus_logging.init_logger(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Kubernetes(cloud.Cloud):
    """Kubernetes cluster."""

    def get_client_configuration(self) -> client.Configuration:
        """Get the client configuration."""
        configuration = client.Configuration()
        configuration.proxy = os.getenv('http_proxy', os.getenv('https_proxy', os.getenv('HTTP_PROXY', os.getenv('HTTPS_PROXY'))))
        if configuration.proxy:
            parsed_proxy_url = parse.urlparse(configuration.proxy)
            configuration.proxy_headers = {
                'Proxy-Authorization': 'Basic ' + base64.b64encode(f'{parsed_proxy_url.username}:{parsed_proxy_url.password}'.encode()).decode()
            }
            configuration.no_proxy = os.getenv('no_proxy', os.getenv('NO_PROXY'))
            configuration.verify_ssl = False
        return configuration

    def get_client(self) -> Type[client.ApiClient]:
        """Get k8s client"""
        client_configuration = self.get_client_configuration()
        config.load_kube_config(config_file=self.auth_config, client_configuration=client_configuration)
        return client.ApiClient(configuration=client_configuration)
    
    def get_core_v1_api(self):
        """Get CoreV1 api"""
        return client.CoreV1Api(self.get_client())

    def get_raycluster_client(self):
        """Get raycluster api"""
        k8s_client = self.get_client()
        try:
            raycluster_api = dynamic.DynamicClient(k8s_client).resources.get(
                api_version="ray.io/v1alpha1", kind="RayCluster"
            )
        except ResourceNotFoundError:
            click.secho("RayCluster CRD not found, KubeRay should be installed first.")
        return raycluster_api

    def get_resources_info(self) -> Tuple[bool, Optional[List[str]]]:
        """Get user group and resources."""
        return True, [self.name, self.cloud_type, self.group or "*", "*"]
    
    def launch_ray(self, ray: RayLaunchParams) -> 'CloudJobInfo':
        """Launch ray compute framework."""
        yaml_path = os.path.join(os.path.expanduser(RAY_CLUSTER_YAML_PREFIX),
                                 f'{ray.framework_id}-{ray.name}.yaml')
        
        user = common_utils.get_current_user()
        ray_cluster_name = common_utils.rfc1035_compliant(
            f'opus-{user}-{ray.name}-{ray.framework_id}' if user else f'opus-anonymous-{ray.name}-{ray.framework_id}'
        )
        setup_command = [common_utils.format_shell_cmds(ray.setupCommand) if ray.setupCommand else '']
        headAcceleratorNum = ray.headAccelerator.split(":")[1] if ray.headAccelerator and ":" in ray.headAccelerator else '0'
        workerAcceleratorNum = ray.workerAccelerator.split(":")[1] if ray.workerAccelerator and ":" in ray.workerAccelerator else '0'
        vars_to_fill = {
            'RAY_CLUSTER_NAME': ray_cluster_name,
            'NAMESPACE': ray.group,
            'SETUP_COMMAND': setup_command,
            'LOAD_ENV': ray.envs if ray.envs != None else {},
            'NUM_WORKER_NODES': ray.workerNum,
            'IMAGE': RAY_IMAGE,
            'NUM_CPUS_OF_HEAD': ray.headCpu,
            'MEM_OF_HEAD': ray.headMem,
            'NUM_ACCELS_OF_HEAD': headAcceleratorNum,
            'RAY_HEAD_NUM_CPUS': ray.headLogicCpu if ray.headLogicCpu != None else ray.headCpu,
            'RAY_HEAD_NUM_GPUS': ray.headLogicGpu if ray.headLogicGpu != None else headAcceleratorNum,
            'RAY_HEAD_CUSTOM_RESOURCES': json.dumps(ray.headCustomResource).replace('"', '\\"') if ray.headCustomResource != None else '{}',
            'NUM_CPUS_PER_WORKER': ray.workerCpu,
            'MEM_PER_WORKER': ray.workerMem,
            'NUM_ACCELS_PER_WORKER': workerAcceleratorNum,
            'RAY_WORKER_NUM_CPUS': ray.workerLogicCpu if ray.workerLogicCpu != None else ray.workerCpu,
            'RAY_WORKER_NUM_GPUS': ray.workerLogicGpu if ray.workerLogicGpu != None else workerAcceleratorNum,
            'RAY_WORKER_CUSTOM_RESOURCES': json.dumps(ray.workerCustomResource).replace('"', '\\"') if ray.workerCustomResource != None else '{}',
            'WORKDIR': ray.workdir
        }

        common_utils.fill_template(RAY_TEMPLATE, vars_to_fill, output_path=yaml_path)
        logger.info(f'{colorama.Fore.YELLOW}The launching script file is located at {yaml_path!r}. {colorama.Style.RESET_ALL}')

        with open(yaml_path, 'r') as f:
            body = yaml.load(f, Loader=yaml.FullLoader)
        try:
            raycluster_api = self.get_raycluster_client()
            # TODO: using apply instead of create would be better
            raycluster_api.create(body=body, namespace=ray.group)
        except Exception as e:
            logger.error(e)
            click.secho("Failed to launch framework <id: {}> on kubernetes {}, Reason: {}"
                        .format(ray.framework_id, self.name, e.reason if hasattr(e, 'reason') else e), fg='red', nl=True)
            sys.exit(1)
        return CloudJobInfo(group=ray.group, job_id=ray_cluster_name)
    
    def is_healthy(self) -> bool:
        """Check the cloud health."""
        try:
            self.get_core_v1_api().get_api_resources()
            return True
        except Exception as e:
            logger.error(f"Kubernetes {self.name} is not available now, error: {e}")
            return False

    def is_job_exist(self, cloud_job_info: CloudJobInfo) -> bool:
        """Check if job exist."""
        try: 
            if cloud_job_info.job_id:
                raycluster_api = self.get_raycluster_client()
                raycluster_api.get(name=cloud_job_info.job_id, namespace=cloud_job_info.group)
        except NotFoundError:
            return False
        except Exception as e:
            logger.info(f"Failed to get framework on kubernetes {cloud_job_info.job_id}, Reason: {e.reason if hasattr(e, 'reason') else e}")
        return True
    
    def is_job_running(self, cloud_job_info: CloudJobInfo) -> bool:
        """Check if cloud job is running."""
        return self.is_ray_ready(cloud_job_info)

    def is_job_failed(self, cloud_job_info: CloudJobInfo) -> bool:
        """Check if job has been failed."""
        ray_head_pod_name = self._get_ray_head_pod_name(cloud_job_info)
        return self._get_pod_status(ray_head_pod_name, cloud_job_info.group) == "Failed"

    def is_ray_ready(self, cloud_job_info: CloudJobInfo) -> bool:
        """Check if the Ray cluster is ready."""
        return self.get_raycluster_details(cloud_job_info).Status == 'ready'

    def get_ray_head_ip(self, cloud_job_info: CloudJobInfo) -> str:
        """Retrieve Head IP of ray that running on the cloud."""
        return self.get_raycluster_details(cloud_job_info).HeadServiceIP

    def _get_ray_head_pod_name(self, cloud_job_info: CloudJobInfo) -> str:
        """Retrieve Head pod name of ray that running on the cloud."""
        core_v1_api = self.get_core_v1_api()
        label_selector = f"ray.io/identifier={cloud_job_info.job_id}-head"
        pods = core_v1_api.list_namespaced_pod(
            cloud_job_info.group, label_selector=label_selector
        )
        if pods.items:
            return pods.items[0].metadata.name
        return None
    
    def _get_pod_status(self, pod_name: str, namespace: str) -> str:
        try:
            api_instance = self.get_core_v1_api()
            pod = api_instance.read_namespaced_pod(name=pod_name, namespace=namespace)
            return pod.status.phase
        except ApiException as e:
            if e.status == 404:
                logger.info("Pod not found")
            else:
                logger.info("Error: " + str(e))
        except Exception as e:
            logger.info("Error: " + str(e))
        return None

    def get_raycluster_details(self, cloud_job_info: CloudJobInfo) -> 'RayClusterDetails':
        """Get raycluster state details."""
        try:
            if cloud_job_info.job_id:
                raycluster_api = self.get_raycluster_client()
                raycluster = raycluster_api.get(name=cloud_job_info.job_id, namespace=cloud_job_info.group)
                return RayClusterDetails(
                    Status=getattr(raycluster.status, "state", None), 
                    HeadServiceIP=raycluster.status.head.serviceIP
                )
        except Exception as e:
            logger.info(f"Failed to get framework on kubernetes {cloud_job_info.job_id}, Reason: {e.reason if hasattr(e, 'reason') else e}")
        return RayClusterDetails(Status=None, HeadServiceIP=None)
    
    def stop_ray(self, cloud_job_info: CloudJobInfo) -> None:
        """Stop ray Framework."""
        raycluster_api = self.get_raycluster_client()
        try:
            raycluster_api.delete(name=cloud_job_info.job_id, namespace=cloud_job_info.group)
            logger.info(f"Stopping Ray cluster: {cloud_job_info.job_id}")
        except Exception as e:
            logger.warn(f"Failed to stop raycluster {cloud_job_info.job_id}, Reason: {e.reason if hasattr(e, 'reason') else e}")
            raise Exception(f"Failed to stop raycluster {cloud_job_info.job_id}, Reason: {e.reason if hasattr(e, 'reason') else e}")

    def ray_head_port_forward(self, cloud_job_info: CloudJobInfo, ray_port: int) -> int:
        """Forward ray port to local."""
        pod_name = self._get_ray_head_pod_name(cloud_job_info)            
        local_port = common_utils.find_free_port()
        cmd = f"kubectl --kubeconfig={self.auth_config} -n {cloud_job_info.group} port-forward pod/{pod_name} {local_port}:{ray_port} --address 0.0.0.0"
        try:
            subprocess.check_output(["kubectl", "--help"])
        except FileNotFoundError:
            logger.error("Error: kubectl command not found.")
            return
        
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

        timeout = 10
        start_time = time.time()
        while not common_utils.is_port_open(local_port):
            if time.time() - start_time > timeout:
                logger.info("Port forwarding process did not start within the timeout period")
                break
            time.sleep(0.1)

        def terminate_process():
            os.killpg(os.getpgid(process.pid), signal.SIGTERM)

        atexit.register(terminate_process)

        return local_port