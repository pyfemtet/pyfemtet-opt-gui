import sys
import logging

_logger = None


def _set_logger():
    global _logger
    if _logger is None:
        _logger = logging.getLogger('GUI')
        _logger.setLevel(logging.INFO)
        _logger.addHandler(logging.StreamHandler(sys.stdout))
        _logger.propagate = False


def get_logger(name: str = None, debug=False):
    _set_logger()

    if name is None:
        logger = _logger

    else:
        logger = logging.getLogger(f'GUI.{name}')

    if debug:
        logger.setLevel(logging.DEBUG)

    return logger
