
import sys
import logging

from time import time, sleep
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger('GUI')
if __name__ == '__main__':
    logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


__all__ = ['Femtet', 'pid', 'connect_femtet', 'check_femtet_alive', 'logger', 'get_parametric_output_names']

Femtet = None
pid = 0


import win32gui
import win32process
import psutil


def _get_hwnds(pid):
    """Proces ID から window handle を取得します."""
    def callback(hwnd, _hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                _hwnds.append(hwnd)
        return True
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds


def _get_pid(hwnd):
    """Window handle から process ID を取得します."""
    if hwnd > 0:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
    else:
        pid = 0
    return pid


def _get_pids(process_name):
    """Process のイメージ名から実行中の process ID を取得します."""
    pids = [p.info["pid"] for p in psutil.process_iter(attrs=["pid", "name"]) if p.info["name"] == process_name]
    return pids


def femtet_exists():
    return len(_get_pids('Femtet.exe')) > 0


def connect_femtet():
    global Femtet, pid

    # logger.setLevel(logging.DEBUG)

    if not check_femtet_alive():
        logger.debug('Femtet is not alive. Try to (re)connect Femtet.')

        from femtetutils import util
        from win32com.client import Dispatch

        succeed = util.auto_execute_femtet(wait_second=15)
        if not succeed:
            logger.error('Failed to launch Femtet successfully.')
            return False

        Femtet = Dispatch('FemtetMacro.Femtet')

        logger.debug('Femtet has launched. wait to establish connection...')
        timeout = 15  # sec
        executor = ThreadPoolExecutor(max_workers=1, )
        future = executor.submit(wait_femtet_connected, *(Femtet, timeout, ))
        return_code = future.result()

        if return_code == 0:
            logger.debug('Connection successfully established.')
            pid = _get_pid(Femtet.hWnd)
            return True

        else:
            logger.error(f'Failed to connect Femtet in {timeout} sec.')
            return False

    else:
        logger.debug(f'Connection is already established.')
        return True


def wait_femtet_connected(Femtet, timeout=15):

    start = time()
    while time() - start < timeout:
        pid = _get_pid(Femtet.hWnd)
        if pid > 0:
            break

        else:
            sleep(1)
    else:
        return 1  # TimeoutError

    return 0  # Succeed


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
    from pyfemtet.opt.interface._femtet_parametric import _get_prm_result_names

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
