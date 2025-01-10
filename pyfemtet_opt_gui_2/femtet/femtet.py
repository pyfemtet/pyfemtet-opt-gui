from threading import Thread
import ctypes
import subprocess
import webbrowser

from femtetutils import util
from win32com.client import Dispatch, CDispatch
import win32process

from pyfemtet_opt_gui_2.logger import get_logger
from pyfemtet_opt_gui_2.common.return_msg import ReturnMsg

logger = get_logger('Femtet')


# global variables per process
_Femtet: 'CDispatch' = None
_dll: 'ctypes.LibraryLoader._dll' = None

__all__ = [
    'get_femtet',
    'get_connection_state',
    'get_obj_names',
    'get_variables',
    'open_help',
]


# ===== Femtet process & object handling =====
def get_femtet():
    global _Femtet

    should_restart_femtet = False

    # Femtet が一度も Dispatch されていない場合
    if _Femtet is None:
        should_restart_femtet = True

    # Femtet が Dispatch されたが現在 alive ではない場合
    elif get_connection_state() != ReturnMsg.no_message:
        should_restart_femtet = True

    # Femtet を再起動する
    if should_restart_femtet:
        logger.info('Femtet を起動しています。')
        util.auto_execute_femtet()

        # Femtet と再接続する (Dispatch は重ね掛け OK)
        logger.info('Femtet との接続を確立しています。')
        _Femtet = Dispatch('FemtetMacro.Femtet')
        # 返答が正常になるまで待つ
        t = Thread(target=_wait_femtet_connected)
        t.start()
        t.join()

    return _Femtet


def _get_pid_from_hwnd(hwnd):
    if hwnd > 0:
        _, pid_ = win32process.GetWindowThreadProcessId(hwnd)
    else:
        pid_ = 0
    return pid_


def _search_femtet():

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    si.wShowWindow = subprocess.SW_HIDE

    image_name = 'Femtet.exe'
    command = f'tasklist /nh /fi "IMAGENAME eq {image_name}"'
    output = subprocess.run(command, startupinfo=si, stdout=subprocess.PIPE, shell=True, text=True)

    is_running = image_name in output.stdout

    return is_running


def get_connection_state() -> ReturnMsg:
    # プロセスが存在しない場合
    if not _search_femtet():
        return ReturnMsg.Error.femtet_not_found

    # Femtet が 1 度も Dispatch されていない場合
    if _Femtet is None:
        return ReturnMsg.Error.femtet_connection_not_yet

    # メソッドへのアクセスを試みる
    try:
        hwnd = _Femtet.hWnd

    # Dispatch オブジェクトは存在するが
    # メソッドにアクセスできない場合
    except Exception:
        return ReturnMsg.Error.femtet_access_error

    # Femtet is now alive
    return ReturnMsg.no_message


def _wait_femtet_connected(timeout=30):
    from time import time, sleep

    start = time()
    while time() - start < timeout:
        hwnd = _Femtet.hWnd
        if hwnd > 0:
            break
        else:
            sleep(0.5)
    else:
        raise TimeoutError(f'Cannot connect to Femtet in {timeout} sec.')

    return hwnd


# ===== ParametricIF handling =====
def _get_dll():
    global _dll

    # assert Femtet connected
    assert get_connection_state() == ReturnMsg.no_message

    # get dll
    if _dll is None:
        femtet_exe_path = util.get_femtet_exe_path()
        dll_path = femtet_exe_path.replace('Femtet.exe', 'ParametricIF.dll')
        _dll = ctypes.cdll.LoadLibrary(dll_path)

    # set Femtet process to dll
    pid = _get_pid_from_hwnd(_Femtet.hWnd)
    _dll.SetCurrentFemtet.restype = ctypes.c_bool
    succeeded = _dll.SetCurrentFemtet(pid)
    if not succeeded:
        logger.error('ParametricIF.SetCurrentFemtet failed')
    return _dll


def get_obj_names() -> tuple[list, ReturnMsg]:
    out = []

    # check Femtet Connection
    ret = get_connection_state()
    if ret != ReturnMsg.no_message:
        return out, ret

    # load dll and set target femtet
    dll = _get_dll()
    n = dll.GetPrmnResult()
    for i in range(n):
        # objective name
        dll.GetPrmResultName.restype = ctypes.c_char_p
        result = dll.GetPrmResultName(i)
        obj_name = result.decode('mbcs')
        # objective value function
        out.append(obj_name)
    return out, ReturnMsg.no_message


if __name__ == '__main__':
    # get Femtet
    Femtet_ = get_femtet()

    # get obj_names
    obj_names, ret_msg = get_obj_names()

    print(ret_msg)
    print(obj_names)


# ===== Parameter =====
def get_variables() -> tuple[dict[str, str | float], ReturnMsg]:
    out = dict()

    # check Femtet Connection
    ret = get_connection_state()
    if ret != ReturnMsg.no_message:
        return out, ret

    # implementation check
    if not hasattr(_Femtet, 'GetVariableNames_py') \
    or not hasattr(_Femtet, 'GetVariableExpression'):
        ret = ReturnMsg.Error.femtet_macro_version_old
        return out, ret

    # get variables
    variable_names = _Femtet.GetVariableNames_py()  # equals or later than 2023.1.1

    # no variables
    if variable_names is None:
        return out, ReturnMsg.no_message

    # succeeded
    for var_name in variable_names:
        expression: str = _Femtet.GetVariableExpression(var_name)

        # check number or expression
        try:
            value = float(expression)
            out[var_name] = value
        except ValueError:
            out[var_name] = expression

    return out, ReturnMsg.no_message


if __name__ == '__main__':
    print(get_variables())


# ===== femtet help homepage =====
def _get_femtet_help_base():
    return 'https://www.muratasoftware.com/products/mainhelp/mainhelp2024_0/desktop/'


def _get_help_url(partial_url):
    # partial_url = 'ParametricAnalysis/ParametricAnalysis.htm'
    # partial_url = 'ProjectCreation/VariableTree.htm'
    return _get_femtet_help_base() + partial_url


def open_help(partial_url):
    webbrowser.open(_get_help_url(partial_url))
