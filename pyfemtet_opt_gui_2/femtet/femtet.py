from threading import Thread
import logging
import ctypes

from femtetutils import util
from win32com.client import Dispatch, CDispatch
import win32process

import pyfemtet_opt_gui_2.logger

logger = logging.getLogger('GUI.femtet')


Femtet: 'CDispatch' = None
pid = 0


def get_pid(hwnd):
    """Window handle から process ID を取得します."""
    global pid

    if hwnd > 0:
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
    else:
        pid = 0
    return pid


def get_femtet():
    global Femtet

    should_refresh_femtet = False

    # Femtet が存在しない場合
    if Femtet is None:
        should_refresh_femtet = True

    # Femtet オブジェクトは存在するが alive ではない場合
    elif not is_femtet_alive(Femtet):
        should_refresh_femtet = True

    if should_refresh_femtet:
        logger.info('Femtet を起動しています。')
        util.auto_execute_femtet()
        Femtet = Dispatch('FemtetMacro.Femtet')

        logger.info('Femtet との接続を確立しています。')
        t = Thread(target=wait_femtet_connected)
        t.start()
        t.join()

    return Femtet


def wait_femtet_connected(timeout=30):
    from time import time, sleep

    start = time()
    while time() - start < timeout:
        hwnd = Femtet.hWnd
        if hwnd > 0:
            break
        else:
            sleep(1)
    else:
        raise TimeoutError(f'Cannot connect to Femtet in {timeout} sec.')

    return hwnd


def is_femtet_alive(_Femtet=None):
    if _Femtet is None:
        _Femtet = Femtet
    _pid = get_pid(_Femtet.hWnd)
    return _pid > 0


def _get_dll():
    femtet_exe_path = util.get_femtet_exe_path()
    dll_path = femtet_exe_path.replace('Femtet.exe', 'ParametricIF.dll')
    return ctypes.cdll.LoadLibrary(dll_path)


def _get_dll_with_set_femtet(Femtet_):
    dll = _get_dll()
    pid = get_pid(Femtet_.hWnd)
    dll.SetCurrentFemtet.restype = ctypes.c_bool
    dll.SetCurrentFemtet(pid)
    return dll


def get_prm_result_names(Femtet_):
    """Used by pyfemtet-opt-gui"""
    out = []

    # load dll and set target femtet
    dll = _get_dll_with_set_femtet(Femtet_)
    n = dll.GetPrmnResult()
    for i in range(n):
        # objective name
        dll.GetPrmResultName.restype = ctypes.c_char_p
        result = dll.GetPrmResultName(i)
        name = result.decode('mbcs')
        # objective value function
        out.append(name)
    return out




if __name__ == '__main__':
    get_femtet()
