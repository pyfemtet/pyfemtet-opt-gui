
from pyfemtet.opt import FemtetInterface, OptunaOptimizer, FEMOpt



def constraint_1(_, opt):
    params = opt.get_parameter()
    w = params['w']
    return w


def constraint_2(_, opt):
    params = opt.get_parameter()
    d = params['d']
    return d


def constraint_3(_, opt):
    params = opt.get_parameter()
    h = params['h']
    return h


def constraint_4(_, opt):
    params = opt.get_parameter()
    r = params['r']
    return r


def main():

    femprj_path = r"C:\Users\mm11592\Documents\myFiles2\working\1_PyFemtetOpt\pyfemtet-opt-gui\pyfemtet_opt_gui\test\test_parametric.femprj"
    model_name = "解析モデル"
    fem = FemtetInterface(
        femprj_path=femprj_path,
        model_name=model_name,
        parametric_output_indexes_use_as_objective={
            0: "maximize",
            1: "maximize",
            2: "maximize",
            3: "maximize",
        },
    )

    femopt = FEMOpt(fem=fem)

    femopt.add_parameter("w", 1.00000000e+00, 0.0, 2.0)
    femopt.add_parameter("d", 8.79558531e-01, -0.12044146899999997, 1.879558531)
    femopt.add_parameter("h", 6.41003511e-01, -0.35899648900000003, 1.641003511)
    femopt.add_constraint(
        fun=constraint_1,
        name="None",
        lower_bound=0,
        upper_bound=None,
        strict=False
    )
    femopt.add_constraint(
        fun=constraint_1,
        name="None",
        lower_bound=0,
        upper_bound=None,
        strict=True
    )
    femopt.add_constraint(
        fun=constraint_1,
        name="qwe1",
        lower_bound=0,
        upper_bound=None,
        strict=False
    )
    femopt.add_constraint(
        fun=constraint_1,
        name="qwe12",
        lower_bound=0,
        upper_bound=None,
        strict=True
    )
    femopt.optimize(
        n_parallel=1,
    )
    
    print('================================')
    print('Finished. Press Enter to quit...')
    print('================================')
    input()

    femopt.terminate_all()

if __name__ == '__main__':
    main()
