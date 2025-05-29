import pyfemtet
print(f' pyfemtet ver{pyfemtet.__version__} imported.')
print()
print('必要なモジュールをインポートしています。しばらくお待ちください。')
print()



# pyfemtet 基本クラス
from pyfemtet.opt import FemtetInterface, FemtetWithSolidworksInterface, OptunaOptimizer, FEMOpt
FemtetInterface._show_parametric_index_warning = False
    
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
        femprj_path=r"",
        model_name="",
        parametric_output_indexes_use_as_objective={}
    )

    opt = OptunaOptimizer(
        sampler_class=RandomSampler,
    )

    femopt = FEMOpt(
        fem=fem,
        opt=opt,
    )




    femopt.optimize(
        n_trials=10,
        timeout=None,
        n_parallel=1,
        confirm_before_exit=False,
        history_path=r"_test_訓練データ.csv",
    )


if __name__ == '__main__':
    main()
