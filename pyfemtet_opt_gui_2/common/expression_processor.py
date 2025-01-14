from numpy import mean
from sympy import sympify

from pyfemtet_opt_gui_2.common.return_msg import ReturnMsg

__all__ = [
    'Expression', 'eval_expressions', 'check_bounds',
]


def check_bounds(value=None, lb=None, ub=None) -> tuple[ReturnMsg, str]:
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

        """
        self.expr: str = str(expression)
        # sympify 時に tuple 扱いになる
        # 日本人が数値に , を使うとき Python では _ を意味する
        # expression に _ が入っていても構わない
        _expr = self.expr.replace(',', '_')
        self._s_expr = sympify(_expr, locals={})

    def is_number(self) -> bool:
        return self._s_expr.is_number

    def is_expression(self) -> bool:
        return not self.is_number()

    @property
    def value(self) -> float:
        if self.is_number():
            return float(self._s_expr)
        else:
            raise ValueError(f'Cannot convert expression {self.expr} to float.')

    def __str__(self):
        return f'{self.expr} ({str(self._s_expr)})'

    def __float__(self):
        return self.value

    def __int__(self):
        return int(float(self))


def eval_expressions(expressions: dict[str, Expression | float | str]) -> tuple[dict[str, float], ReturnMsg]:
    #  値渡しに変換
    expressions = expressions.copy()

    out = dict()
    error_keys = []

    for key, expression in expressions.items():
        if isinstance(expression, Expression):
            expressions[key] = expression.expr

    expression: str | float
    for key, expression in expressions.items():
        evaluated = sympify(
            expression,
            locals={
                'mean': lambda *args: mean(args),
                # 'std': lambda *args: std(args),  # doesn't work
                'max': max,
                'min': min,
            }
        ).subs(expressions)

        try:
            value = float(evaluated)

        except Exception:  # mostly TypeError
            value = None
            error_keys.append(key)

        out[key] = value

    if error_keys:
        return {}, ReturnMsg.Error.evaluated_expression_not_float + f': {error_keys}'

    else:
        return out, ReturnMsg.no_message


if __name__ == '__main__':

    expressions_: dict[str, Expression] = {
        'section_radius': Expression(0.5),
        'coil_radius': Expression("section_radius * coil_height"),
        'coil_pitch': Expression("exp(2.0**2)"),
        'n': Expression(3.0),
        'coil_radius_grad': Expression(0.1),
        'gap': Expression('current * 2 + sympy'),
        'current': 1.0,
        'coil_height': 'sqrt(coil_pitch * (n))',
        'sympy': 0,
        'test': "mean(1, 2, 3)",
        'test2': "max(1, 2, 3)",
        'test3': "min(1, 2, 3)",
        'test4': "min(1., 2., 3.)",
    }

    evaluated_, ret_msg = eval_expressions(expressions_)
    print(ret_msg)
    for key_, value_ in evaluated_.items():
        print(key_, value_)
