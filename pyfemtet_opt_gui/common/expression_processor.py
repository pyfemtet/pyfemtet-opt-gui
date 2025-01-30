from sympy import sympify
from sympy.core.sympify import SympifyError
from sympy import Min, Max, Add, Symbol

from pyfemtet_opt_gui.common.return_msg import ReturnMsg

__all__ = [
    'Expression', 'eval_expressions', 'check_bounds', 'SympifyError'
]


def get_valid_functions(expressions=None):
    return {
        'mean': lambda *args: Add(*args).subs(expressions if expressions is not None else {}) / len(args),
        'max': Max,
        'min': Min,
        'S': Symbol('S')
    }


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

        # max(name1, name2) など関数を入れる際に問題になるので
        # 下記の仕様は廃止
        # # sympify 時に tuple 扱いになるので , を置き換える
        # # 日本人が数値に , を使うとき Python では _ を意味する
        # # expression に _ が入っていても構わない
        # tmp_expr = str(self._expr).replace(',', '_')
        tmp_expr = self._expr
        try:
            self._s_expr = sympify(tmp_expr, locals=get_valid_functions())
            self.is_valid = True
        except SympifyError as e:
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
        return self._s_expr.is_number

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
            return float(self._s_expr)
        else:
            raise ValueError(f'Cannot convert expression {self.expr} to float.')

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f'{self.expr} ({str(self._s_expr)})'

    def __float__(self):
        return self.value

    def __int__(self):
        return int(float(self))


def eval_expressions(expressions: dict[str, Expression | float | str]) -> tuple[dict[str, float], ReturnMsg, str]:
    #  値渡しに変換
    expressions = expressions.copy()

    out = dict()
    error_keys = []

    for key, expression in expressions.items():
        if isinstance(expression, Expression):
            expressions[key] = expression.expr

    expression: str | float
    for key, expression in expressions.items():

        sympified = sympify(
            expression,
            locals=get_valid_functions(expressions),
        )

        if isinstance(sympified, tuple):
            value = None
            error_keys.append(key)

        else:
            evaluated = sympified.subs(expressions)
            try:
                value = float(evaluated)

            except TypeError:  # mostly TypeError or ValueError
                value = None
                error_keys.append(key)

        out[key] = value

    if error_keys:
        return {}, ReturnMsg.Error.evaluated_expression_not_float, f': {error_keys}'

    else:
        return out, ReturnMsg.no_message, ''


if __name__ == '__main__':

    expressions_: dict[str, Expression] = {
        'section_radius': Expression(0.5),
        'coil_radius': Expression("section_radius * coil_height"),
        'coil_pitch': Expression("exp(2.0**2)"),
        'n': Expression(3.0),
        'coil_radius_grad': Expression(0.1),
        'gap': Expression('current * 2 + sympy'),
        'current': 'n',
        'coil_height': 'sqrt(coil_pitch * (n))',
        'sympy': 0,
        'test': "mean(gap, 2, 3)",
        'test2': "max(1, 2, 3)",
        'test3': "min(current, 2, 3)",
        'test4': "min(1., 2., 3.)",
    }

    evaluated_, ret_msg, additional_msg = eval_expressions(expressions_)
    for key_, value_ in evaluated_.items():
        print(key_, value_)
    print(ret_msg)
