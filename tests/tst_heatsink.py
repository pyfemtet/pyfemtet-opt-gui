import pyfemtet
print(f' pyfemtet ver{pyfemtet.__version__} imported.')
print()
print('必要なモジュールをインポートしています。しばらくお待ちください。')
print()


# pyfemtet 基本クラス
from pyfemtet.opt import FemtetInterface, FemtetWithSolidworksInterface, OptunaOptimizer, FEMOpt

# サロゲートモデル作成用クラス
from pyfemtet.opt.interface import PoFBoTorchInterface

# 最適化アルゴリズム
from pyfemtet.opt.optimizer import PoFBoTorchSampler
from optuna.samplers import RandomSampler, QMCSampler, NSGAIISampler, TPESampler
from optuna_integration import BoTorchSampler

# Femtet の書式で書かれた式を Python の書式に変換する関数群
from numpy import mean, max, min, pi, sin, cos, tan, arctan, log, sqrt, abs

def _femtet_operator_core(b: bool):
    return -1 if b else 0

def _femtet_equal(a, b):
    return _femtet_operator_core(a == b)

def _femtet_not_equal(a, b):
    return _femtet_operator_core(a != b)

def _femtet_less_than(a, b):
    return _femtet_operator_core(a < b)

def _femtet_less_than_equal(a, b):
    return _femtet_operator_core(a <= b)

def _femtet_greater_than(a, b):
    return _femtet_operator_core(a > b)

def _femtet_greater_than_equal(a, b):
    return _femtet_operator_core(a >= b)

def _femtet_operator_and(*args):
    ret = int(args[0])
    for arg in args[1:]:
        ret = ret & int(arg)
    return ret

def _femtet_operator_or(*args):
    ret = int(args[0])
    for arg in args[1:]:
        ret = ret | int(arg)
    return ret

def _femtet_f_if(condition, if_true_or_else, if_false_or_zero):
    if not isinstance(condition, bool):
        condition = condition != _femtet_operator_core(False)
    return if_true_or_else if condition else if_false_or_zero
FUNC_NAME_TO_FUNC = {_femtet_equal.__name__: _femtet_equal, _femtet_not_equal.__name__: _femtet_not_equal, _femtet_less_than.__name__: _femtet_less_than, _femtet_less_than_equal.__name__: _femtet_less_than_equal, _femtet_greater_than.__name__: _femtet_greater_than, _femtet_greater_than_equal.__name__: _femtet_greater_than_equal, _femtet_operator_and.__name__: _femtet_operator_and, _femtet_operator_or.__name__: _femtet_operator_or}

def get_femtet_builtins(d: dict=None) -> dict:
    d = d or {}
    d.update({'mean': lambda *args: float(mean(args)), 'max': lambda *args: float(max(args)), 'min': lambda *args: float(min(args)), 'pi': pi, 'sin': sin, 'cos': cos, 'tan': tan, 'atn': arctan, 'log': log, 'sqr': sqrt, 'abs': abs, 'f_if': _femtet_f_if})
    d.update(FUNC_NAME_TO_FUNC)
    return d

print('モジュールのインポートが完了しました。')
print('最適化が開始されると、ブラウザのプロセスモニターが自動的に起動します。')
print(f'======================')


# 最適化のメイン関数
def main():

    fem = FemtetInterface(
        femprj_path=r"C:\Users\mm11592\Documents\myFiles2\working\pyfemtet\pyfemtet-opt-gui\tests\test_heatsink.femprj",
        model_name="250521_奇数偶数判定あり",
        parametric_output_indexes_use_as_objective={0: "minimize", 1: "minimize"}
    )

    opt = OptunaOptimizer(
        sampler_class=TPESampler,
        sampler_kwargs={"n_startup_trials": 10}
    )

    femopt = FEMOpt(
        fem=fem,
        opt=opt,
        history_path="最適化_20250528_090420.csv",
    )

    femopt.add_parameter(
        name="w",
        initial_value=50.0,
        lower_bound=45.0,
        upper_bound=55.00000000000001,
    )
    femopt.add_parameter(
        name="l",
        initial_value=30.0,
        lower_bound=27.0,
        upper_bound=33.0,
    )
    femopt.add_parameter(
        name="h",
        initial_value=10.0,
        lower_bound=9.0,
        upper_bound=11.0,
    )
    femopt.add_parameter(
        name="d",
        initial_value=3.0,
        lower_bound=2.7,
        upper_bound=3.3000000000000003,
    )
    femopt.add_parameter(
        name="num_x",
        initial_value=5.0,
        lower_bound=4.5,
        upper_bound=5.5,
    )
    femopt.add_parameter(
        name="num_y",
        initial_value=5.0,
        lower_bound=4.5,
        upper_bound=5.5,
    )
    femopt.add_expression(
        name="dis_x",
        fun=lambda w, num_x, d: eval("((w-2*d)-(num_x*d))/(num_x-1)", dict(**locals(), **get_femtet_builtins())),
        pass_to_fem=False,
    )
    femopt.add_expression(
        name="pitch_x",
        fun=lambda dis_x, d: eval("dis_x+d", dict(**locals(), **get_femtet_builtins())),
        pass_to_fem=False,
    )
    femopt.add_expression(
        name="dis_y",
        fun=lambda l, num_y, d: eval("((l-2*d)-(num_y*d))/(num_y-1)", dict(**locals(), **get_femtet_builtins())),
        pass_to_fem=False,
    )
    femopt.add_expression(
        name="pitch_y",
        fun=lambda dis_y, d: eval("dis_y+d", dict(**locals(), **get_femtet_builtins())),
        pass_to_fem=False,
    )
    femopt.add_parameter(
        name="inner_d",
        initial_value=4.0,
        lower_bound=3.6,
        upper_bound=4.4,
    )
    femopt.add_parameter(
        name="board_t",
        initial_value=0.5,
        lower_bound=0.45,
        upper_bound=0.55,
    )
    femopt.add_parameter(
        name="vol",
        initial_value=0.001,
        lower_bound=0.0009000000000000001,
        upper_bound=0.0011,
    )
    femopt.add_parameter(
        name="temp",
        initial_value=40.0,
        lower_bound=36.0,
        upper_bound=44.0,
    )



    femopt.optimize(
        n_trials=10,
        timeout=None,
        n_parallel=1,
    )


if __name__ == '__main__':
    main()
