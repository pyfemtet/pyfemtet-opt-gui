import os
import ctypes
import webbrowser
import ast

import psutil
from femtetutils import util
from win32com.client import Dispatch, CDispatch
# noinspection PyUnresolvedReferences
from pythoncom import com_error
import win32process

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from PySide6.QtCore import QCoreApplication

import pyfemtet_opt_gui
from pyfemtet_opt_gui.logger import get_logger
from pyfemtet_opt_gui.common.return_msg import ReturnMsg, ReturnType
from pyfemtet_opt_gui.common.expression_processor import Expression
from pyfemtet_opt_gui.common.type_alias import *
from pyfemtet_opt_gui.fem_interfaces.base_fem_interface import AbstractFEMInterface
from pyfemtet_opt_gui.fem_interfaces.femtet_interface.femtet_expression_support import *


logger = get_logger('Femtet')

# global variables per process
_Femtet: CDispatch | None = None
_dll: 'ctypes.LibraryLoader._dll' = None
CONNECTION_TIMEOUT = 15


def _get_pid_from_hwnd(hwnd):
    if hwnd > 0:
        _, pid_ = win32process.GetWindowThreadProcessId(hwnd)
    else:
        pid_ = 0
    return pid_


def _search_process(process_name):
    is_running = False

    try:
        for proc in psutil.process_iter():
            if process_name == proc.name():
                is_running = True
                break

    # psutil が失敗する場合はプロセス存在の
    # エラーチェックをあきらめる
    except Exception:  # noqa
        is_running = True

    return is_running


# 比較演算子に対応する関数名
COMPARE_OP_TO_FUNC_NAME: dict[type, str] = {
    ast.Eq: _femtet_equal.__name__,
    ast.NotEq: _femtet_not_equal.__name__,
    ast.Lt: _femtet_less_than.__name__,
    ast.LtE: _femtet_less_than_equal.__name__,
    ast.Gt: _femtet_greater_than.__name__,
    ast.GtE: _femtet_greater_than_equal.__name__,
    ast.And: _femtet_operator_and.__name__,
    ast.Or: _femtet_operator_or.__name__,
}


# Femtet の比較演算子に合わせるための
# 文字列中の比較演算を関数に変換するための
# transformer
class CompareTransformer(ast.NodeTransformer):

    def visit_BoolOp(self, node: ast.BoolOp):
        op_type = type(node.op)
        if op_type in COMPARE_OP_TO_FUNC_NAME:
            func_name = COMPARE_OP_TO_FUNC_NAME[op_type]
            node = ast.Call(
                func=ast.Name(id=func_name, ctx=ast.Load()),
                args=node.values,
                keywords=[]
            )

        return self.generic_visit(node)

    def visit_Compare(self, node: ast.Compare):
        if len(node.ops) == 1 and len(node.comparators) == 1:
            op_type = type(node.ops[0])

            # 変換対象かどうか
            if op_type in COMPARE_OP_TO_FUNC_NAME:
                func_name = COMPARE_OP_TO_FUNC_NAME[op_type]

                node = ast.Call(
                    func=ast.Name(id=func_name, ctx=ast.Load()),
                    args=[node.left, node.comparators[0]],
                    keywords=[]
                )

        return self.generic_visit(node)


class FemtetInterfaceGUI(AbstractFEMInterface):

    # ===== Femtet process & object handling =====
    @classmethod
    def get_fem(cls, progress: QProgressDialog | None = None) -> tuple[CDispatch | None, ReturnType]:
        global _Femtet

        if progress is not None:
            progress.setLabelText(QCoreApplication.translate(
                "pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui",
                "Femtet を起動しています...",
            ))

        should_restart_femtet = False

        # Femtet が一度も Dispatch されていない場合
        if _Femtet is None:
            should_restart_femtet = True

        # Femtet が Dispatch されたが現在 alive ではない場合
        elif FemtetInterfaceGUI.get_connection_state() != ReturnMsg.no_message:
            should_restart_femtet = True

        # Femtet を再起動する
        if should_restart_femtet:
            logger.info(QCoreApplication.translate(
                "pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui",
                "Femtet を起動しています。",
            ))

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

    @classmethod
    def _search_femtet(cls):
        return _search_process('Femtet.exe')

    @classmethod
    def get_connection_state(cls) -> ReturnType:
        # プロセスが存在しない場合
        if not cls._search_femtet():
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
        except Exception:  # noqa
            return ReturnMsg.Error.femtet_access_error

        # メソッドにアクセスできるが
        # hwnd が 0 である状態
        if hwnd == 0:
            return ReturnMsg.Error.femtet_access_error

        # Femtet is now alive
        return ReturnMsg.no_message

    # ===== ParametricIF handling =====
    @classmethod
    def _get_dll(cls):
        global _dll

        # assert Femtet connected
        assert FemtetInterfaceGUI.get_connection_state() == ReturnMsg.no_message

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

    @classmethod
    def get_obj_names(cls) -> tuple[list, ReturnType]:
        out = []

        # check Femtet Connection
        ret = FemtetInterfaceGUI.get_connection_state()
        if ret != ReturnMsg.no_message:
            return out, ret

        # load dll and set target femtet
        dll = cls._get_dll()
        n = dll.GetPrmnResult()
        for i in range(n):
            # objective name
            dll.GetPrmResultName.restype = ctypes.c_char_p
            result = dll.GetPrmResultName(i)
            obj_name = result.decode('mbcs')
            # objective value function
            out.append(obj_name.replace(' / ', '\n'))
        return out, ReturnMsg.no_message

    # ===== Parameter =====
    @classmethod
    def get_variables(cls) -> tuple[
        dict[VariableName, Expression],
        ReturnType
    ]:
        out = dict()

        # check Femtet Connection
        ret = FemtetInterfaceGUI.get_connection_state()
        if ret != ReturnMsg.no_message:
            return {}, ret

        # implementation check
        if (
                not hasattr(_Femtet, 'GetVariableNames_py')
                or not hasattr(_Femtet, 'GetVariableExpression')
        ):
            return {}, ReturnMsg.Error.femtet_macro_version_old

        # get variables
        variable_names: tuple[str, ...] | None = _Femtet.GetVariableNames_py()  # equals or later than 2023.1.1

        # no variables
        if variable_names is None:
            return out, ReturnMsg.no_message

        # exclude `pi` or `c_pi`
        variable_names = tuple([name for name in variable_names
                                if name not in ('pi', 'c_pi')])

        # no variables
        if len(variable_names) == 0:
            return out, ReturnMsg.no_message

        # succeeded
        for var_name in variable_names:
            expression: str = _Femtet.GetVariableExpression(var_name)
            try:
                norm_var_name = cls.normalize_var_name(var_name)
                out[VariableName(
                    raw=var_name,
                    converted=norm_var_name
                )] = Expression(
                    expression,
                    variable_names
                )
            except Exception:  # noqa
                return {}, ReturnMsg.Error.cannot_recognize_as_an_expression

        return out, ReturnMsg.no_message

    @classmethod
    def apply_variables(
            cls,
            variables: dict[
                RawVariableName,
                float
            ]
    ) -> tuple[ReturnType, str | None]:
        # check Femtet Connection
        ret = FemtetInterfaceGUI.get_connection_state()
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
                additional_msg = QCoreApplication.translate(
                    "pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui",
                    "変数: {var_name}, 値: {value}",
                ).format(var_name=var_name, value=value)
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
            additional_msg = QCoreApplication.translate(
                "pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui",
                "マクロ名: `UpdateVariable` エラーメッセージ: {exception_msg}",
            ).format(exception_msg=exception_msg)

        r_msg2, a_msg2 = cls._rebuild_model()
        if r_msg2 != ReturnMsg.no_message:
            return r_msg2, a_msg2

        # except から finally に来ていれば
        # すでに return_msg が入っている
        return return_msg, additional_msg

    # ===== Expression Processing =====
    @classmethod
    def normalize_expr_str(
            cls,
            expr_str: RawExpressionStr,
            names: list[RawVariableName],
    ) -> ConvertedExpressionStr:

        # 退避
        expr_str = expr_str.replace("<=", "<$$")
        expr_str = expr_str.replace('>=', '>$$')
        expr_str = expr_str.replace('==', '$$$$')

        # 変換
        expr_str = expr_str.replace('=', '==')
        expr_str = expr_str.replace('<>', '!=')
        expr_str = expr_str.replace('^', '**')

        # 元に戻す
        expr_str = expr_str.replace('<$$', '<=')
        expr_str = expr_str.replace('>$$', '>=')
        expr_str = expr_str.replace('$$$$', '==')

        # 特定の演算子を関数に変換
        tree = ast.parse(expr_str, mode="eval")
        transformer = CompareTransformer()
        new_tree = transformer.visit(tree)
        ast.fix_missing_locations(new_tree)
        expr_str = ast.unparse(new_tree)

        # 変数名を convert
        out = expr_str
        for name in names:
            out.replace(name, cls.normalize_var_name(name))

        return out

    @classmethod
    def normalize_var_name(
        cls,
        name: RawVariableName,
    ) -> ConvertedVariableName:
        return (
            name
            .replace('.', '__dot__')
            .replace('@', '__at__')
            .replace('-', '__hyphen__')
        )

    @classmethod
    def unnormalize_var_name(
            cls,
            name: ConvertedVariableName,
    ) -> RawVariableName:
        return (
            name
            .replace('__dot__', '.')
            .replace('__at__', '@')
            .replace('__hyphen__', '-')
        )

    # ===== Modeling =====
    @classmethod
    def _rebuild_model(cls) -> tuple[ReturnType, str | None]:
        # モデルを再構築
        # Gaudi にアクセスするだけで失敗する場合もある
        # ここで失敗したらどうしようもない
        try:
            _Femtet.Gaudi.Activate()  # always returns None
            succeeded = _Femtet.Gaudi.ReExecute()
            if not succeeded:
                _Femtet.ShowLastError()
            _Femtet.Redraw()  # always returns None

            return ReturnMsg.no_message, None

        except Exception as e:  # com_error or NoAttribute
            exception_msg = ' '.join([str(a) for a in e.args])
            additional_msg = QCoreApplication.translate(
                "pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui",
                "マクロ名: ReExecute, エラーメッセージ: {exception_msg}",
            ).format(exception_msg=exception_msg)
            return ReturnMsg.Error.femtet_macro_failed, additional_msg

    @classmethod
    def _get_last_x_t_path(cls) -> tuple[ReturnType, str | None]:
        """
        Returns:
            ReturnMsg, x_t_path
        """

        # check Connection
        ret = FemtetInterfaceGUI.get_connection_state()
        if ret != ReturnMsg.no_message:
            return ret, None

        x_t_path = _Femtet.Gaudi.LastXTPath

        if x_t_path == '':
            return ReturnMsg.Error.femtet_no_cad_import,  None

        return ReturnMsg.no_message, x_t_path

    @classmethod
    def _set_last_x_t_path(cls, x_t_path) -> ReturnType:
        """
        Returns:
            ReturnMsg
        """

        # check Connection
        ret = FemtetInterfaceGUI.get_connection_state()
        if ret != ReturnMsg.no_message:
            return ret

        _Femtet.Gaudi.LastXTPath = x_t_path

        ret, *_ = cls._rebuild_model()
        return ret

    # ===== femtet help homepage =====
    @classmethod
    def _get_fem_help_base(cls):
        return 'https://www.muratasoftware.com/products/mainhelp/mainhelp2024_0/desktop/'

    @classmethod
    def _get_help_url(cls, partial_url):
        # partial_url = 'ParametricAnalysis/ParametricAnalysis.htm'
        # partial_url = 'ProjectCreation/VariableTree.htm'
        return cls._get_fem_help_base() + partial_url

    @classmethod
    def open_help(cls, partial_url):
        webbrowser.open(cls._get_help_url(partial_url))

    # ===== project handling =====
    @classmethod
    def get_name(cls) -> tuple[tuple[list[str | None], str], ReturnType]:
        """
        Returns:
            (file_paths, model_name), return_msg
        """

        # check Femtet Connection
        ret = FemtetInterfaceGUI.get_connection_state()
        if ret != ReturnMsg.no_message:
            return ([None], ''), ret

        # check something opened
        if _Femtet.Project == '':
            return ([QCoreApplication.translate(
                "pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui",
                "解析プロジェクトが開かれていません",
            ),], ''), ReturnMsg.no_message

        # else, return them
        return ([_Femtet.Project,], _Femtet.AnalysisModelName), ReturnMsg.no_message

    @classmethod
    def save_femprj(cls) -> tuple[bool, tuple[ReturnType, str]]:
        a_msg = ''

        # check Femtet Connection
        ret = FemtetInterfaceGUI.get_connection_state()
        if ret != ReturnMsg.no_message:
            return False, (ret, a_msg)

        (femprj_paths, model_name), ret = cls.get_name()
        if ret != ReturnMsg.no_message:
            return False, (ret, a_msg)
        femprj_path = femprj_paths[0]

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

    @classmethod
    def open_sample(cls, progress: QProgressDialog | None = None) -> tuple[ReturnType, str]:

        if progress is not None:
            progress.setLabelText(QCoreApplication.translate(
                "pyfemtet_opt_gui.fem_interfaces.femtet_interface_gui",
                "Femtet のサンプルファイルを開いています...",
            ))

        # get path
        # noinspection PyTypeChecker
        path = os.path.abspath(
            os.path.join(
                os.path.dirname(pyfemtet_opt_gui.__file__),
                'assets', 'samples', 'sample.femprj'
            )
        ).replace(os.path.altsep, os.path.sep)

        # check Femtet Connection
        ret = FemtetInterfaceGUI.get_connection_state()
        if ret != ReturnMsg.no_message:
            return ret, path

        succeeded = _Femtet.LoadProject(path, True)
        if not succeeded:
            return ReturnMsg.Error.cannot_open_sample_femprj, path

        return ReturnMsg.no_message, path

    @classmethod
    def _load_femprj(cls, path):
        succeeded = _Femtet.LoadProject(path, True)
        return succeeded


if __name__ == '__main__':
    # get Femtet
    Femtet_, ret_msg = FemtetInterfaceGUI.get_fem()
    if ret_msg != ReturnMsg.no_message:
        print(ret_msg)
        print(FemtetInterfaceGUI.get_connection_state())
        from sys import exit

        exit()

    else:
        # get obj_names
        obj_names, ret_msg = FemtetInterfaceGUI.get_obj_names()

        print(ret_msg)
        print(obj_names)

    FemtetInterfaceGUI.open_sample()
    print(FemtetInterfaceGUI.get_variables())
