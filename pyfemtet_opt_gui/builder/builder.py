import json

__all__ = [
    'create_header',
    'create_footer',
    'create_main',
    'create_command_line',
    'create_message',
]

INDENT = '    '


def ind(n_indent):
    return INDENT * n_indent


# pyfemtet.__version__ 等
def create_message():
    code = '''
import pyfemtet
print(f' pyfemtet ver{pyfemtet.__version__} imported.')
print()
print('必要なモジュールをインポートしています。しばらくお待ちください。')
print()
'''[1:]
    return code


# import 文
def create_header():
    code = '''
# pyfemtet 基本クラス
from pyfemtet.opt import FemtetInterface, FemtetWithSolidworksInterface, OptunaOptimizer, FEMOpt

# 最適化アルゴリズム
from pyfemtet.opt.optimizer import PoFBoTorchSampler
from optuna.samplers import RandomSampler, QMCSampler, NSGAIISampler, TPESampler
from optuna_integration import BoTorchSampler

# mean 関数
from statistics import mean as _mean
mean = lambda *args: _mean(args)

print('モジュールのインポートが完了しました。')
print('最適化が開始されると、ブラウザのプロセスモニターが自動的に起動します。')
print(f'======================')
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


# each command
def create_command_line(command_json, n=1):
    """
    Available object:
        command = dict(
            command='function', # str
            args=dict(arg1=1), # (optional) dict
            ret=a, # (optional) str
        )

        or

        function = dict(
            function: str,
            args: (optional) dict,
            commands: list[command],
            ret: (optional) str
        )

    """

    # reconstruct
    _command = json.loads(command_json)

    # function def or not
    if 'function' in _command.keys():
        return _create_function_def(command_json, n)

    assert isinstance(_command, dict)
    assert 'command' in _command.keys()

    # set default values
    command = dict(
        ret=None,
    )
    command.update(_command)

    # function or not
    if 'args' in command.keys():

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
            if isinstance(value, list | tuple):
                # key=(elem1, elem2,)
                code += ind(n + 1) + f'{key}=(' + ', '.join(value) + ',)\n'
            elif isinstance(value, dict):
                # key={k: v, k2: v2}
                arr = [f'{k}: {v}' for k, v in value.items()]
                code += ind(n + 1) + key + '={' + ', '.join(arr) + '}\n'
            else:
                code += ind(n + 1) + f'{key}={value},\n'

        # )
        if len(kwargs) == 0:
            assert code.endswith(f'{function}(\n')
            code = code.replace(f'{function}(\n', f'{function}()\n')
        else:
            code += ind(n) + ')\n'

    else:

        # create
        line: str = command['command']
        ret: str | None = command['ret']

        if ret is None:
            code = ind(n) + line + '\n'
        else:
            code = ind(n) + ret + ' = ' + line + '\n'

    return code


# def function
def _create_function_def(command_json, n):
    # reconstruct
    _command = json.loads(command_json)
    assert isinstance(_command, dict)
    assert 'function' in _command.keys()

    # default values
    func_def = dict(
        args=[],
        kwargs={},
        commands=None,
        ret=None,
    )
    func_def.update(_command)

    # def func_name(arg, kwarg=None, kwarg2=1):
    args = func_def['args']
    args.extend([f'{k}={v}' for k, v in func_def['kwargs'].items()])

    code = ind(n) + f'def {func_def["function"]}(' + ', '.join(args) + '):\n'

    # body
    if func_def['commands'] is None:
        code += ind(n + 1) + 'pass\n'

    else:
        for cmd_ in func_def['commands']:
            code += create_command_line(json.dumps(cmd_), n + 1)

    # return
    if func_def['ret'] is not None:
        code += ind(n + 1) + f'return {func_def["ret"]}\n'

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

    g_code = ''

    g_code += create_header()
    g_code += '\n'
    g_code += '\n'
    g_code += create_main()
    g_code += create_command_line(g_command_json)
    g_code += '\n'
    g_code += '\n'
    g_code += create_footer()

    print(g_code)
