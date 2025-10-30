from __future__ import annotations

import sys
import ast
from traceback import print_exception
from graphlib import TopologicalSorter
from typing import Sequence, Any

import unicodedata

from pyfemtet_opt_gui.common.return_msg import ReturnMsg, ReturnType
from pyfemtet_opt_gui.fem_interfaces.femtet_interface.femtet_expression_support import (
    get_fem_builtins as get_femtet_builtins
)
from pyfemtet_opt_gui.fem_interfaces.solidworks_interface.solidworks_expression_support import (
    get_fem_builtins as get_solidworks_builtins,
    split_unit_solidworks
)
from pyfemtet_opt_gui.common.type_alias import *

from pyfemtet_opt_gui.fem_interfaces import (
    get as get_fem_class,
    get_current_cad_name,
    CADIntegration
)
from PySide6.QtCore import QCoreApplication


__all__ = [
    'Expression',
    'eval_expressions',
    'check_bounds',
    'check_expr_str_and_bounds',
    'ExpressionParseError',
]


class NotSupportedOperatorError(Exception):
    pass


class ExpressionParseError(Exception):
    pass


def check_bounds(value=None, lb=None, ub=None) -> tuple[ReturnType, str | None]:
    if value is None:
        if lb is None:
            return ReturnMsg.no_message, None
        else:
            if ub is None:
                return ReturnMsg.no_message, None
            else:
                if ub >= lb:
                    return ReturnMsg.no_message, None
                else:
                    return ReturnMsg.Error.inconsistent_lb_ub, f'lower: {lb}\nupper: {ub}'
    else:
        if lb is None:
            if ub is None:
                return ReturnMsg.no_message, None
            else:
                if value <= ub:
                    return ReturnMsg.no_message, None
                else:
                    return ReturnMsg.Error.inconsistent_value_ub, f'value: {value}\nupper: {ub}'
        else:
            if ub is None:
                if lb <= value:
                    return ReturnMsg.no_message, None
                else:
                    return ReturnMsg.Error.inconsistent_value_lb, f'lower: {lb}\nvalue: {value}'
            else:
                if lb <= value <= ub:
                    return ReturnMsg.no_message, None
                elif lb > value:
                    return ReturnMsg.Error.inconsistent_value_lb, f'lower: {lb}\nvalue: {value}'
                elif value > ub:
                    return ReturnMsg.Error.inconsistent_value_ub, f'value: {value}\nupper: {ub}'
                else:
                    raise NotImplementedError


def check_expr_str_and_bounds(
        expr_str: RawExpressionStr | None,
        lb: float | None,
        ub: float | None,
        expressions: dict[VariableName, Expression],
) -> tuple[ReturnType, str]:

    raw_var_names = [n.raw for n in expressions.keys()]

    # 両方とも指定されていなければエラー
    if lb is None and ub is None:
        return ReturnMsg.Error.no_bounds, ''

    # 上下関係がおかしければエラー
    if lb is not None and ub is not None:
        ret_msg, a_msg = check_bounds(None, lb, ub)
        if ret_msg != ReturnMsg.no_message:
            return ret_msg, a_msg

    # expression が None ならエラー
    if expr_str is None:
        return (
            ReturnMsg.Error.cannot_recognize_as_an_expression,
            QCoreApplication.translate(
                'pyfemtet_opt_gui.common.expression_processor',
                '式が入力されていません。'
            )
        )

    # expression が None でなくとも
    # Expression にできなければエラー
    try:
        _expr = Expression(expr_str, raw_var_names=raw_var_names)
    except ExpressionParseError:
        return ReturnMsg.Error.cannot_recognize_as_an_expression, expr_str

    # Expression にできても値が
    # 計算できなければエラー
    _tmp_expr_key_name = 'this_is_a_target_constraint_expression'
    _expr_key = VariableName(
        raw=_tmp_expr_key_name,
        converted=_tmp_expr_key_name,
    )
    expressions.update(
        {_expr_key: _expr}
    )
    ret, ret_msg, a_msg = eval_expressions(expressions)
    a_msg = a_msg.replace(_tmp_expr_key_name, expr_str)
    if ret_msg != ReturnMsg.no_message:
        return ret_msg, a_msg

    # Expression の計算ができても
    # lb, ub との上下関係がおかしければ
    # Warning
    if _expr_key not in ret.keys():
        raise RuntimeError(f'Internal Error! The _expr_key '
                           f'({_expr_key}) is not in ret.keys() '
                           f'({tuple(ret.keys())})')
    if not isinstance(ret[_expr_key], float):
        raise RuntimeError(f'Internal Error! The type of '
                           f'ret[_expr_key] is not float '
                           f'but {type(ret[_expr_key])}')
    evaluated = ret[_expr_key]
    ret_msg, a_msg = check_bounds(evaluated, lb, ub)
    if ret_msg != ReturnMsg.no_message:
        return ReturnMsg.Warn.inconsistent_value_bounds, ''

    # 何もなければ no_msg
    return ReturnMsg.no_message, ''


def get_dependency(expr_str: ConvertedExpressionStr) -> set[ConvertedVariableName]:
    """大文字・小文字を維持したまま依存変数を取得する。
    関数は無視する。"""

    # CAD ビルトイン関数名の小文字化したもの
    cad_builtin_keys_lower = [key.lower() for key in get_cad_builtins().keys()]

    try:
        # 式のASTを生成
        tree = ast.parse(expr_str, mode='eval')

        dependent_vars = set()
        used_functions = set()

        class Validator(ast.NodeVisitor):
            def visit_Name(self, node: ast.Name):
                # 変数名を収集
                # dependent_vars.add(node.id)  # 元のコードで半角ｶﾀｶﾅが全角に変換されてしまう
                # https://docs.python.org/ja/3.10/library/ast.html#ast.AST.end_col_offset
                b = expr_str.split('\n')[node.lineno - 1].encode("utf-8")
                dependent_vars.add(b[node.col_offset: node.end_col_offset].decode("utf-8"))

            def visit_Call(self, node: ast.Call):
                # 関数呼び出しをチェック
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    used_functions.add(func_name)
                    # 大文字・小文字は任意のものが入ってくるので
                    # チェック対象との比較のため小文字化
                    if func_name.lower() not in cad_builtin_keys_lower:
                        raise ExpressionParseError(f"Invalid function used: {func_name}")
                else:
                    # 例えば属性アクセスなどは許可しない
                    raise ExpressionParseError("Only simple function names are allowed")
                self.generic_visit(node)

        Validator().visit(tree)

        # locals は除く
        dependent_vars = {v for v in dependent_vars if v.lower() not in cad_builtin_keys_lower}

        # 関数を除く
        dependent_vars = dependent_vars - used_functions

        return dependent_vars

    except Exception as e:
        print_exception(e)
        raise ExpressionParseError(expr_str) from e


def get_cad_builtins():
    # TODO: FEM クラスに移動
    current_cad = get_current_cad_name()
    if current_cad == CADIntegration.solidworks:
        return get_solidworks_builtins()
    elif current_cad == CADIntegration.no:
        return get_femtet_builtins()
    else:
        assert False, f'Unknown CADIntegration: {current_cad}'


class Expression:

    expr_str: RawExpressionStr | float
    raw_var_names: Sequence[RawVariableName] | None
    unit: str
    norm_expr_str: ConvertedExpressionStr
    norm_dependencies: set[ConvertedVariableName]

    def __init__(
            self,
            expr_str: RawExpressionStr | float,
            raw_var_names: Sequence[RawVariableName],
    ):
        """
        Example:
            e = Expression('1')
            e.expr  # '1'
            e.value  # 1.0

            e = Expression(1)
            e.expr  # '1'
            e.value  # 1.0

            e = Expression('a')
            e.expr  # 'a'
            e.value  # ValueError

            e = Expression('1/2')
            e.expr  # '1/2'
            e.value  # 0.5

            e = Expression('1.0000')
            e.expr  # '1.0'
            e.value  # 1.0

        """

        # 元の変数名リストを保存
        self.expr_str = expr_str
        self.raw_var_names = raw_var_names

        # 最低限の整形
        self.norm_expr_str = str(self.expr_str).strip()

        # 単位があれば分離
        # TODO: FEM クラスに統合する
        self.unit = ''
        if get_current_cad_name() == CADIntegration.solidworks:
            no_unit, unit = split_unit_solidworks(self.norm_expr_str)
            self.norm_expr_str = no_unit
            self.unit = unit  # '', 'mm', ...

        # 書式を python で評価できる形に変換
        # FEM クラスに依存する正規化
        try:
            self.norm_expr_str = get_fem_class().normalize_expr_str(
                self.norm_expr_str,
                raw_var_names
            )
        except Exception as e:
            self.is_valid = False
            raise ExpressionParseError(str(e)) from e

        # 正規化できたら dependency を取得
        try:
            self.norm_dependencies = get_dependency(self.norm_expr_str)
            self.is_valid = True
        except ExpressionParseError as e:
            self.is_valid = False
            raise e

        # 適切な locals を与えれば Python 式として評価できる文字列
        # 大文字・小文字を区別しないが変更しては不具合が出る CAD のため
        # Python 評価時は小文字で統一
        self.norm_expr_str_ready_to_eval: ConvertedExpressionStr = \
            self.norm_expr_str.lower()

    def _get_value_if_pure_number(self) -> float | None:
        # 1.0000 => True
        # 1 * 0.9 => False
        # 100mm => False
        if self.unit != '':
            return None
        try:
            value = float(str(self.expr_str).replace(',', '_'))
            return value
        except ValueError:
            return None

    def is_number(self) -> bool:
        return len(self.norm_dependencies) == 0

    def is_expression(self) -> bool:
        return not self.is_number()

    @property
    def expr_display(self) -> str:
        # 1.0000000e+0 などは 1 などにする
        # ただし 1.1 * 1.1 などは 1.21 にしない
        # self.is_number() は後者も True を返す
        value = self._get_value_if_pure_number()
        if value is not None:
            return str(value)
        else:
            return str(self.expr_str)

    @property
    def value(self) -> float:
        if self.is_number():
            return self.eval()
        else:
            raise ValueError(f'Cannot convert expression {self.expr_display} to float.')

    def eval(self, locals_: dict[str, Any] = None):
        # locals の組立
        l_ = {k.lower(): v for k, v in get_cad_builtins().items()}
        if locals_ is not None:
            l_.update({k.lower(): v for k, v in locals_.items()})

        # 半角カナが入っていてもいいように評価時のみ正規化する
        return float(
            eval(
                unicodedata.normalize('NFKC', self.norm_expr_str_ready_to_eval),
                {unicodedata.normalize('NFKC', key): value for key, value in l_.items()}
            )
        )

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.expr_display} ({str(self.expr_str)})'

    def __float__(self):
        return self.value

    def __int__(self):
        return int(float(self))


def topological_sort(expressions: dict[VariableName, Expression]) -> list[ConvertedVariableName]:
    """
    Raises:
        CycleError
    """
    dependencies: dict[ConvertedVariableName, set[ConvertedVariableName]] = \
        {name.converted: expr.norm_dependencies for name, expr in expressions.items()}
    ts = TopologicalSorter(dependencies)
    return list(ts.static_order())


def eval_expressions(
        expressions: dict[VariableName, Expression | float | RawExpressionStr]
) -> tuple[dict[VariableName, float], ReturnType, str]:

    # 値渡しに変換
    expressions = expressions.copy()

    # 戻り値を準備
    error_keys = []

    # value の型を Expression に統一
    raw_var_names = [var_name.raw for var_name in expressions.keys()]
    for key, expression_ in expressions.items():
        if isinstance(expression_, Expression):
            pass
        elif isinstance(expression_, float | RawExpressionStr):
            expressions[key] = Expression(expression_, raw_var_names)
        else:
            assert False, f'Type of expression_ is invalid: {expression_}({type(expression_)}).'

    # 不明な変数を参照していればエラー
    expression: Expression
    for key, expression in expressions.items():
        for var_name in expression.norm_dependencies:
            if var_name not in [n.converted for n in expressions.keys()]:
                error_keys.append(f"{key.raw}: {var_name}")  # error!

    # エラーがあれば終了
    if len(error_keys) > 0:
        return {}, ReturnMsg.Error.unknown_var_name, f': {error_keys}'

    # トポロジカルソート
    evaluation_order = topological_sort(expressions)

    # ソート順に評価
    norm_var_name_to_var_name = {n.converted: n for n in expressions.keys()}
    evaluated_locals: dict[ConvertedVariableName, float] = {}
    out: dict[VariableName, float] = {}
    for norm_var_name in evaluation_order:

        # 評価
        key: VariableName = norm_var_name_to_var_name[norm_var_name]
        expression = expressions[key]
        try:
            value = expression.eval(evaluated_locals)
        except Exception as e:
            print_exception(e)
            print(f'Failed to evaluate expression '
                  f'{key.raw}={expression.norm_expr_str_ready_to_eval}',
                  file=sys.stderr)
            # 評価に失敗（これ以降が計算できないのでここで終了）
            error_keys.append(key.raw)  # error!
            break

        # 評価済み変数に追加
        evaluated_locals[key.converted] = value
        out[key] = value

    if error_keys:
        return {}, ReturnMsg.Error.evaluated_expression_not_float, f': {error_keys}'

    else:
        return out, ReturnMsg.no_message, ''
