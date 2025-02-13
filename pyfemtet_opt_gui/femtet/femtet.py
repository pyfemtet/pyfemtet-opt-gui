import ctypes
import subprocess
import webbrowser

import psutil
import psutil
from femtetutils import util
from win32com.client import Dispatch, CDispatch
# noinspection PyUnresolvedReferences
from pythoncom import com_error
import win32process

from pyfemtet_opt_gui.logger import get_logger
from pyfemtet_opt_gui.common.return_msg import ReturnMsg
from pyfemtet_opt_gui.common.expression_processor import Expression

logger = get_logger('Femtet')


# global variables per process
_Femtet: 'CDispatch' = None
_dll: 'ctypes.LibraryLoader._dll' = None
CONNECTION_TIMEOUT = 15

__all__ = [
    'get_femtet',
    'get_connection_state',
    'get_obj_names',
    'get_variables',
    'apply_variables',
    'open_help',
    'get_name',
    'save_femprj',
]


# ===== Femtet process & object handling =====
def get_femtet() -> tuple[CDispatch | None, ReturnMsg]:
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

        # 内部で Dispatch 実行も行うので
        # その可否も含め接続成功判定が可能
        succeeded = util.auto_execute_femtet(wait_second=CONNECTION_TIMEOUT)
        _Femtet = Dispatch('FemtetMacro.Femtet')

    else:
        succeeded = True

    if succeeded:
        return _Femtet, ReturnMsg.no_message

    else:
        return None, ReturnMsg.Error.femtet_connection_failed


def _get_pid_from_hwnd(hwnd):
    if hwnd > 0:
        _, pid_ = win32process.GetWindowThreadProcessId(hwnd)
    else:
        pid_ = 0
    return pid_


def _search_femtet():

    is_running = False

    try:
        process_name = 'Femtet.exe'
        for proc in psutil.process_iter():
            if process_name == proc.name():
                is_running = True
                break

    # psutil が失敗する場合はプロセス存在の
    # エラーチェックをあきらめる
    except Exception:
        is_running = True

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
    # (makepy できていない？)
    except Exception:
        return ReturnMsg.Error.femtet_access_error

    # メソッドにアクセスできるが
    # hwnd が 0 である状態
    if hwnd == 0:
        return ReturnMsg.Error.femtet_access_error

    # Femtet is now alive
    return ReturnMsg.no_message


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
        out.append(obj_name.replace(' / ', '\n'))
    return out, ReturnMsg.no_message


if __name__ == '__main__':
    # get Femtet
    Femtet_, ret_msg = get_femtet()
    if ret_msg != ReturnMsg.no_message:
        print(ret_msg)
        print(get_connection_state())
        from sys import exit
        exit()

    else:
        # get obj_names
        obj_names, ret_msg = get_obj_names()

        print(ret_msg)
        print(obj_names)


# ===== Parameter =====
def get_variables() -> tuple[dict[str, Expression], ReturnMsg]:
    out = dict()

    # check Femtet Connection
    ret = get_connection_state()
    if ret != ReturnMsg.no_message:
        return {}, ret

    # implementation check
    if (
            not hasattr(_Femtet, 'GetVariableNames_py')
            or not hasattr(_Femtet, 'GetVariableExpression')
    ):
        return {}, ReturnMsg.Error.femtet_macro_version_old

    # get variables
    variable_names = _Femtet.GetVariableNames_py()  # equals or later than 2023.1.1

    # no variables
    if variable_names is None:
        return out, ReturnMsg.no_message

    # succeeded
    for var_name in variable_names:
        expression: str = _Femtet.GetVariableExpression(var_name)
        try:
            out[var_name] = Expression(expression)
        except Exception:
            return {}, ReturnMsg.Error.cannot_recognize_as_an_expression

    return out, ReturnMsg.no_message


def apply_variables(variables: dict[str, float | str]) -> tuple[ReturnMsg, str | None]:

    # check Femtet Connection
    ret = get_connection_state()
    if ret != ReturnMsg.no_message:
        return ret, None

    # implementation check
    if not hasattr(_Femtet, 'UpdateVariable'):
        return ReturnMsg.Error.femtet_macro_version_old, None

    # 型 validation
    _variables = dict()
    for var_name, value in variables.items():
        try:
            value = float(value)
            _variables.update({var_name: value})
        except ValueError:
            additional_msg = f'変数: {var_name}, 値: {value}'
            return ReturnMsg.Error.not_a_number, additional_msg
    variables: dict[str, float] = _variables

    # UpdateVariable に失敗した場合でも
    # ReExecute と Redraw はしないといけないので
    # try-except-finally を使う
    return_msg = ReturnMsg.no_message
    additional_msg = None
    try:
        # variables ごとに処理
        for var_name, value in variables.items():
            # float にはすでにしているので Femtet に転送
            succeeded = _Femtet.UpdateVariable(
                var_name, value
            )

            # 実行結果チェック
            if not succeeded:
                # com_error が必ず起こる
                _Femtet.ShowLastError()
    except com_error as e:
        return_msg = ReturnMsg.Error.femtet_macro_failed
        exception_msg = ' '.join([str(a) for a in e.args])
        additional_msg = (f'マクロ名: `UpdateVariable` '
                          f'エラーメッセージ: {exception_msg}')

    finally:

        # モデルを再構築
        # Gaudi にアクセスするだけで失敗する場合もある
        # ここで失敗したらどうしようもない
        try:
            _Femtet.Gaudi.Activate()  # always returns None
            succeeded = _Femtet.Gaudi.ReExecute()
            if not succeeded:
                _Femtet.ShowLastError()
            _Femtet.Redraw()  # always returns None


        except Exception as e:  # com_error or NoAttribute
            exception_msg = ' '.join([str(a) for a in e.args])
            additional_msg = (f'マクロ名: ReExecute, '
                              f'エラーメッセージ: {exception_msg}')
            return ReturnMsg.Error.femtet_macro_failed, additional_msg

        # except から finally に来ていれば
        # すでに return_msg が入っている
        return return_msg, additional_msg


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


# ===== project handling =====
def get_name() -> tuple[tuple[str, str] | None, ReturnMsg]:

    # check Femtet Connection
    ret = get_connection_state()
    if ret != ReturnMsg.no_message:
        return None, ret

    # check something opened
    if _Femtet.Project == '':
        return ('解析プロジェクトが開かれていません', ''), ReturnMsg.no_message

    # else, return them
    return (_Femtet.Project, _Femtet.AnalysisModelName), ReturnMsg.no_message


def save_femprj() -> tuple[bool, tuple[ReturnMsg, str]]:
    a_msg = ''

    # check Femtet Connection
    ret = get_connection_state()
    if ret != ReturnMsg.no_message:
        return False, (ret, a_msg)

    (femprj_path, model_name), ret = get_name()
    if ret != ReturnMsg.no_message:
        return False, (ret, a_msg)

    # SaveProject(ProjectFile As String, bForce As Boolean) As Boolean
    succeeded = _Femtet.SaveProject(femprj_path, True)
    if not succeeded:
        ret = ReturnMsg.Error.femtet_save_failed
        a_msg = 'Error message: '
        try:
            Femtet_.ShowLastError()
        except Exception as e:
            a_msg += ' '.join(e.args)
        return False, (ret, a_msg)

    return True, (ReturnMsg.no_message, a_msg)
