from pyfemtet_opt_gui.common.expression_processor import Expression, eval_expressions


def test_1():
    expressions_: dict[str, Expression] = {
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

    evaluated_, ret_msg, additional_msg = eval_expressions(expressions_)
    for key_, value_ in evaluated_.items():
        print(key_, value_)
    print(ret_msg)


def test_2():
    expressions_: dict[str, Expression] = {
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

    evaluated_, ret_msg, additional_msg = eval_expressions(expressions_)
    for key_, value_ in evaluated_.items():
        print(key_, value_)
    print(ret_msg, additional_msg)


if __name__ == '__main__':
    test_1()
    test_2()
