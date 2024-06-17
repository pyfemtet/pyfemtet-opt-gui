
from pyfemtet.opt import FemtetInterface, OptunaOptimizer, FEMOpt


def main():

    femprj_path = r"C:\Users\mm11592\Documents\myFiles2\working\1_PyFemtetOpt\pyfemtet-opt-gui\pyfemtet_opt_gui\test\test_parametric.femprj"
    model_name = "解析モデル"
    fem = FemtetInterface(
        femprj_path=femprj_path,
        model_name=model_name,
        parametric_output_indexes_use_as_objective={
            2: "maximize",
            3: "maximize",
        },
    )

    femopt = FEMOpt(fem=fem)

    femopt.add_parameter("d", 8.79558531e-01, -0.12044146899999997, 1.879558531)
    femopt.optimize(
        timeout=180.0,
        n_parallel=1,
    )
    femopt.terminate_all()

if __name__ == '__main__':
    main()
