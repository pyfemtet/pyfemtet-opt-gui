
from pyfemtet.opt import FemtetInterface, OptunaOptimizer, FEMOpt


def main():

    femprj_path = r"E:\pyfemtet\pyfemtet\tests\test_5_ParametricIF\test_parametric.femprj"
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

    femopt.add_parameter("w", 1.52275251e-01, -0.8477247489999999, 1.152275251)
    femopt.add_parameter("d", 8.79558531e-01, -0.12044146899999997, 1.879558531)
    femopt.add_parameter("h", 6.41003511e-01, -0.35899648900000003, 1.641003511)
    femopt.optimize(
        n_parallel=1,
    )
    femopt.terminate_all()

if __name__ == '__main__':
    main()
