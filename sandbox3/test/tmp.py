
from pyfemtet.opt import FemtetInterface, OptunaOptimizer, FEMOpt


def main():

    femprj_path = r"E:\pyfemtet\pyfemtet-opt-gui\sandbox3\test\test_parametric.femprj"
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

    femopt.add_parameter("w", 9.73205594e-01, -0.02679440600000005, 1.973205594)
    femopt.add_parameter("d", 1.33703782e+00, 0.33703781999999993, 2.33703782)
    femopt.add_parameter("h", -2.30749711e-01, -1.230749711, 0.769250289)
    femopt.optimize(
        n_trials=10,
        n_parallel=1,
    )
    femopt.terminate_all()

if __name__ == '__main__':
    main()
