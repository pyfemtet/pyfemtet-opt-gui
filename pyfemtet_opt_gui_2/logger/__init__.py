import sys
import logging

_logger = logging.getLogger('GUI')
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler(sys.stdout))


def get_module_logger(name: str, debug=False):
    logger = logging.getLogger(f'GUI.{name}')
    if debug:
        logger.setLevel(logging.DEBUG)
    return logger
