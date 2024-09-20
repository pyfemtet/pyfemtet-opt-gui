from pyfemtet.dispatch_extensions import (
    dispatch_femtet, launch_and_dispatch_femtet, DispatchExtensionException,
    _get_pids, _get_pid)
from pyfemtet.logger import get_logger
from pyfemtet.opt.interface._femtet_parametric import _get_prm_result_names

logger = get_logger('Wiz')


__all__ = ['Femtet', 'pid', 'connect_femtet', 'check_femtet_alive', 'logger', 'get_parametric_output_names']

Femtet = None
pid = 0


def connect_femtet():
    global Femtet, pid

    # check existing femtet
    pids = _get_pids('Femtet.exe')

    try:

        # launch new Femtet if no Femtet
        if len(pids) == 0:
            Femtet, pid = launch_and_dispatch_femtet(
                strictly_pid_specify=False
            )

        # try to connect existing Femtet if exists
        else:
            Femtet, pid = dispatch_femtet()

        # if ome problem has occurred, do version check
        if pid <= 0:
            return False

        if ...:  # Femtet.Version >= 2023.1
            return True


    except DispatchExtensionException as e:

        return False


def check_femtet_alive() -> bool:
    global Femtet, pid

    # Femtet is None
    if Femtet is None:
        Femtet, pid = None, 0
        return False

    # IFemtet existed, but its process is dead.
    current_pid = _get_pid(Femtet.hWnd)
    if current_pid <= 0:
        Femtet, pid = None, 0
        return False

    # IFemtet connects existing femtet, update pid
    pid = current_pid

    return True


def get_parametric_output_names():
    return _get_prm_result_names(Femtet)


# class _Dummy:
#     def __init__(self):
#         self.pid = 1
#         self.prj = r'c:\some\file.prj'
#         self.pid = 'some-model'
#
#     def get_prm_names(self):
#         return ['p1', 'p2', 'p3']
#
#     def get_prm_expressions(self):
#         return [1, 'p1+p2', '3.1415926563']
#
#     def get_output_names(self):
#         return ['out1', 'out2', 'out3', 'out4']
#
#
# Femtet = _Dummy()
