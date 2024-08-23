"""Logging utils"""
import logging
import sys
import os
import re
from logging.handlers import TimedRotatingFileHandler

_FORMAT = '%(levelname).1s | %(asctime)s | %(filename)s:%(lineno)d -- %(message)s'
_DATE_FORMAT = '%y-%m-%d %H:%M:%S'


class NewLineFormatter(logging.Formatter):
    """Adds logging prefix to newlines to align multi-line messages."""

    def __init__(self, fmt, datefmt=None):
        logging.Formatter.__init__(self, fmt, datefmt)

    def format(self, record):
        msg = logging.Formatter.format(self, record)
        if record.message != '':
            parts = msg.split(record.message)
            msg = msg.replace('\n', '\r\n' + parts[0])
        return msg
    

_root_logger = logging.getLogger('opus')
_stream_handler = logging.StreamHandler(sys.stdout)
log_dir = '~/.opus/opus_logs'
log_path = os.path.join(os.path.expanduser(log_dir), 'opus.log')
os.makedirs(os.path.dirname(log_path), exist_ok=True)
_file_handler = TimedRotatingFileHandler(filename=log_path,
                                         when='MIDNIGHT',
                                         interval=1,
                                         backupCount=30)
_file_handler.suffix = '%Y-%m-%d.log'
_file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}.log$")


def _setup_logger():
    _root_logger.setLevel(logging.DEBUG)
    fmt = NewLineFormatter(fmt=_FORMAT, datefmt=_DATE_FORMAT)
    _stream_handler.flush = sys.stdout.flush
    _stream_handler.setLevel(logging.INFO)
    _stream_handler.setFormatter(fmt)
    _file_handler.setLevel(logging.DEBUG)
    _file_handler.setFormatter(fmt)
    _root_logger.addHandler(_stream_handler)
    _root_logger.addHandler(_file_handler)
    # Setting this will avoid the message
    # being propagated to the parent logger.
    _root_logger.propagate = False


# The logger is initialized when the module is imported.
_setup_logger()


def init_logger(name: str):
    return logging.getLogger(name)