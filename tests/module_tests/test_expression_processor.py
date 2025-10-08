from pyfemtet_opt_gui.common.return_msg import ReturnMsg
import pyfemtet_opt_gui.fem_interfaces  # noqa  # expression_processor の import error の暫定対策
from pyfemtet_opt_gui.common.expression_processor import Expression, eval_expressions


def test_1():
    expressions: dict[str, Expression] = {
        'section_radius': Expression(0.5),
        'coil_radius': Expression("section_radius * coil_height"),
        'coil_pitch': Expression("log(2.0**2)"),
        'n': Expression(3.0),
        'coil_radius_grad': Expression(0.1),
        'gap': Expression('current * 2 + sympy'),
        'current': Expression('n'),
        'coil_height': Expression('sqr(coil_pitch * (n))'),
        'sympy': Expression(0),
        'test': Expression("mean(gap, 2, 3)"),
        'test2': Expression("max(1, 2, 3)"),
        'test3': Expression("min(current, 2, 3)"),
        'test4': Expression("min(1., 2., 3.)"),
    }

    evaluated, ret_msg, additional_msg = eval_expressions(expressions)
    print(evaluated)

    assert ret_msg == ReturnMsg.no_message
    assert evaluated == {'section_radius': 0.5, 'coil_pitch': 1.3862943611198906, 'n': 3.0, 'coil_radius_grad': 0.1, 'sympy': 0.0, 'test2': 3.0, 'test4': 1.0, 'current': 3.0, 'coil_height': 2.039333980337618, 'gap': 6.0, 'test3': 2.0, 'coil_radius': 1.019666990168809, 'test': 3.6666666666666665}


def test_2():
    expressions: dict[str, Expression] = {
        'n': Expression(5),
        'n_is_odd': Expression('((n/2) and 1) = 0'),
        'mid_n': Expression('F_IF(n_is_odd, (n+1)/2, n/2)'),
        'mid_n_direct': Expression('F_IF(((n/2) and 1) = 0, (n+1)/2, n/2)'),
        'm': Expression(6),
        'm_is_odd': Expression('((m/2) and 1) = 0'),
        'mid_m': Expression('F_IF(m_is_odd, (m+1)/2, m/2)'),
        'mid_m_direct': Expression('F_IF(((m/2) and 1) = 0, (m+1)/2, m/2)'),
        'use_pi': Expression('sin(pi/4) ^ 2')
    }

    evaluated, ret_msg, additional_msg = eval_expressions(expressions)
    print(evaluated)

    assert ret_msg == ReturnMsg.no_message
    assert evaluated == {'n': 5.0, 'm': 6.0, 'use_pi': 0.5000000000000001, 'n_is_odd': -1.0, 'mid_n_direct': 3.0, 'm_is_odd': 0.0, 'mid_m_direct': 3.0, 'mid_n': 3.0, 'mid_m': 3.0}


if __name__ == '__main__':
    # test_1()
    test_2()
