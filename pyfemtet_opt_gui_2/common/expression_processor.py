from numpy import mean
from sympy import sympify

from pyfemtet_opt_gui_2.common.return_msg import ReturnMsg


def eval_expressions(expressions: dict[str, str | float]) -> tuple[dict[str, float], ReturnMsg]:

    out = dict()
    error_keys = []

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

    expressions_: dict[str, str | float] = {
        'section_radius': 0.5,
        'coil_radius': "section_radius * coil_height",
        'coil_pitch': "exp(2.0**2)",
        'n': 3.0,
        'coil_radius_grad': 0.1,
        'gap': 'current * 2 + sympy',
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
