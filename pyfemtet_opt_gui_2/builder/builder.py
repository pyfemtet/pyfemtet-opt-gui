import json

__all__ = [
    'create_header',
    'create_footer',
    'create_main',
    'create_command_line',
    'create_femopt'
]

INDENT = '    '


def ind(n_indent):
    return INDENT * n_indent


# import 文
def create_header():
    code = '''
# pyfemtet 基本クラス
from pyfemtet.opt import FemtetInterface, OptunaOptimizer, FEMOpt

# 最適化アルゴリズム
from pyfemtet.opt.optimizer import PoFBoTorchSampler
from optuna.samplers import RandomSampler, QMCSampler, NSGAIISampler, TPESampler
from optuna_integration import BoTorchSampler

# mean 関数
from statistics import mean as _mean
mean = lambda *args: _mean(args)
'''[1:]
    return code


# if __name__ == '__main__':
def create_footer():
    code = '''
if __name__ == '__main__':
    main()
'''[1:]
    return code


# def main():
def create_main():
    code = f'''
# 最適化のメイン関数
def main():
'''[1:]

    return code


# femopt = FEMOpt(fem, opt)
def create_femopt(n_indent=1):
    code = f'''
{ind(n_indent)}femopt = FEMOpt(fem=fem, opt=opt)
    '''[1:]

    return code


# each command
def create_command_line(command_json, n=1):
    # reconstruct
    _command = json.loads(command_json)
    assert isinstance(_command, dict)
    assert 'command' in _command.keys()

    # default values
    command = dict(
        args=dict(),
        ret=None,
    )
    command.update(_command)

    # create
    function: str = command['command']
    _kwargs: dict = command['args']
    ret: str | None = command['ret']

    # kwargs の value が dict なら
    # その key が int なら int にする
    def convert(kwargs__, new_kwargs):
        for key__, value__ in kwargs__.items():
            if isinstance(value__, dict):
                new_value__ = {}
                convert(value__, new_value__)
                kwargs__[key__] = new_value__
                value__ = new_value__
            try:
                key__ = int(key__)
            except ValueError:
                pass
            finally:
                new_kwargs[key__] = value__

    kwargs = {}
    convert(_kwargs, kwargs)

    # function(\n
    code = ind(n) + f'{f"{ret} = " if ret is not None else ""}{function}(\n'

    for key, value in kwargs.items():
        #     key=value,\n
        code += ind(n + 1) + f'{key}={value},\n'

    # )
    code += ind(n) + ')\n'

    return code


if __name__ == '__main__':
    # sample command
    command_object = dict(
        command='femopt.add_parameter',
        args=dict(
            name='"parameter 1"',
            initial_value=0.,
            lower_bound=-1.,
            upper_bound=1.,
            pass_to_fem=False,
            step=None,
        ),
        ret=None
    )

    # sample command
    command_object = dict(
        command='FEMOpt',
        args=dict(
            fem='fem',
            opt='opt',
        ),
        ret='femopt'
    )

    # sample command
    command_object = dict(
        ret='fem',
        command='FemtetInterface',
        args=dict(
            femprj_path='"sample.femprj"',
            model_name='"sample"',
            parametric_output_indexes_use_as_objective={
                0: 'minimize',
                1: 0.
            }
        ),
    )

    g_command_json = json.dumps(command_object)

    create_command_line(g_command_json)

    code = ''

    code += create_header()
    code += '\n'
    code += '\n'
    code += create_main()
    code += create_command_line(g_command_json)
    code += '\n'
    code += '\n'
    code += create_footer()

    print(code)
