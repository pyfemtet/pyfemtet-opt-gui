from __future__ import annotations

import sys
import ast
from traceback import print_exception
from graphlib import TopologicalSorter

from pyfemtet_opt_gui.common.return_msg import ReturnMsg, ReturnType
from pyfemtet_opt_gui.common.femtet_operator_support import *


__all__ = [
    'Expression',
    'eval_expressions',
    'check_bounds',
    'check_expr_str_and_bounds',
    'ExpressionParseError',
]


class NotSupportedOperatorError(Exception):
    pass


# 比較演算子に対応する関数名
COMPARE_OP_TO_FUNC_NAME = {
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


# Femtet 式を Python 書式・Femtet 演算に変換
def convert_operator(expr_str: str) -> str:
    # 小文字に統一
    expr_str = expr_str.lower()

    # 退避
    expr_str = expr_str.replace('<=', '<$$')
    expr_str = expr_str.replace('>=', '>$$')

    # 変換
    expr_str = expr_str.replace('=', '==')
    expr_str = expr_str.replace('<>', '!=')
    expr_str = expr_str.replace('^', '**')

    # 元に戻す
    expr_str = expr_str.replace('<$$', '<=')
    expr_str = expr_str.replace('>$$', '>=')

    # 演算子を関数に変換
    tree = ast.parse(expr_str, mode='eval')
    transformer = CompareTransformer()
    new_tree = transformer.visit(tree)
    ast.fix_missing_locations(new_tree)
    return ast.unparse(new_tree)


class ExpressionParseError(Exception):
    pass


def check_bounds(value=None, lb=None, ub=None) -> tuple[ReturnMsg, str | None]:
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
        expr_str: str | None,
        lb: float | None,
        ub: float | None,
        expressions: dict[str, Expression],
) -> tuple[ReturnType, str]:

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
        return ReturnMsg.Error.cannot_recognize_as_an_expression, '式が入力されていません。'

    # expression が None でなくとも
    # Expression にできなければエラー
    try:
        _expr = Expression(expr_str)
    except ExpressionParseError:
        return ReturnMsg.Error.cannot_recognize_as_an_expression, expr_str

    # Expression にできても値が
    # 計算できなければエラー
    _expr_key = 'this_is_a_target_constraint_expression'
    # expressions = var_model.get_current_variables()
    expressions.update(
        {_expr_key: _expr}
    )
    ret, ret_msg, a_msg = eval_expressions(expressions)
    a_msg = a_msg.replace(_expr_key, expr_str)
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


def get_dependency(expr_str):
    try:
        # 式のASTを生成
        tree = ast.parse(expr_str, mode='eval')

        dependent_vars = set()
        used_functions = set()

        class Validator(ast.NodeVisitor):
            def visit_Name(self, node: ast.Name):
                # 変数名を収集
                dependent_vars.add(node.id)

            def visit_Call(self, node: ast.Call):
                # 関数呼び出しをチェック
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    used_functions.add(func_name)
                    if func_name not in get_femtet_builtins():
                        raise ExpressionParseError(f"Invalid function used: {func_name}")
                else:
                    # 例えば属性アクセスなどは許可しない
                    raise ExpressionParseError("Only simple function names are allowed")
                self.generic_visit(node)

        Validator().visit(tree)

        # locals は除く
        dependent_vars = dependent_vars - set(get_femtet_builtins().keys())

        return dependent_vars

    except Exception as e:
        print_exception(e)
        raise ExpressionParseError(str(e)) from e


def remove_prefix_recursive(string, prefix):
    while string.startswith(prefix):
        string = string.removeprefix(prefix)
    return string


class Expression:

    def __init__(self, expression: str | float):
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
        # ユーザー指定の何らかの入力
        self._expr: str | float = expression

        # 最低限の整形を行う
        if isinstance(self._expr, str):
            self._expr = remove_prefix_recursive(self._expr, ' ')

        # femtet 書式を python 書式に変換
        try:
            self._converted_expr_str: str = convert_operator(str(self._expr))
        except Exception as e:
            self.is_valid = False
            raise ExpressionParseError(str(e)) from e

        # 変換できたら dependency を取得
        try:
            self.dependencies = get_dependency(self._converted_expr_str)
            self.is_valid = True

        except ExpressionParseError as e:
            self.is_valid = False
            raise e

    def _get_value_if_pure_number(self) -> float | None:
        # 1.0000 => True
        # 1 * 0.9 => False
        try:
            value = float(str(self._expr).replace(',', '_'))
            return value
        except ValueError:
            return None

    def is_number(self) -> bool:
        return len(self.dependencies) == 0

    def is_expression(self) -> bool:
        return not self.is_number()

    @property
    def expr(self) -> str:
        # 1.0000000e+0 などは 1 などにする
        # ただし 1.1 * 1.1 などは 1.21 にしない
        # self.is_number() は後者も True を返す
        value = self._get_value_if_pure_number()
        if value is not None:
            return str(value)
        else:
            return self._expr

    @property
    def value(self) -> float:
        if self.is_number():
            return float(eval(self._converted_expr_str))
        else:
            raise ValueError(f'Cannot convert expression {self.expr} to float.')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.expr} ({str(self._expr)})'

    def __float__(self):
        return self.value

    def __int__(self):
        return int(float(self))


def topological_sort(expressions: dict[str, Expression]) -> list[str]:
    """
    Raises:
        CycleError
    """
    dependencies = {name: expr.dependencies for name, expr in expressions.items()}
    ts = TopologicalSorter(dependencies)
    return list(ts.static_order())


def eval_expressions(expressions: dict[str, Expression | float | str]) -> tuple[dict[str, float], ReturnType, str]:

    # 値渡しに変換
    expressions_ = expressions.copy()

    error_keys = []

    # 型を統一
    expression_: str | float | Expression
    for key, expression_ in expressions_.items():
        if not isinstance(expression_, Expression):
            expressions[key] = Expression(expression_)

    # 不明な変数を参照していればエラー
    expression: Expression
    for key, expression in expressions.items():
        for var_name in expression.dependencies:
            if var_name not in expressions:
                error_keys.append(key)  # error!

    # エラーがあれば終了
    if len(error_keys) > 0:
        return {}, ReturnMsg.Error.unknown_var_name, f': {error_keys}'

    # トポロジカルソート
    evaluation_order = topological_sort(expressions)

    # ソート順に評価
    evaluated_value = {}
    for key in evaluation_order:

        # 評価の中で使える locals を作成
        l = get_femtet_builtins()
        l.update(evaluated_value)

        # 評価
        expression = expressions[key]
        try:
            value = float(eval(str(expression._converted_expr_str), l))
        except Exception as e:
            print_exception(e)
            print('expression:', expression._converted_expr_str, file=sys.stderr)
            # 評価に失敗（これ以降が計算できないのでここで終了）
            error_keys.append(key)  # error!
            break

        # 評価済み変数に追加
        evaluated_value[key] = value

    if error_keys:
        return {}, ReturnMsg.Error.evaluated_expression_not_float, f': {error_keys}'

    else:
        return evaluated_value, ReturnMsg.no_message, ''
