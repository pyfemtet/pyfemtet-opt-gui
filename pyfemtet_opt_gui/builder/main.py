import json
import os
import enum
import re
from packaging.version import Version

import pyfemtet

from pyfemtet_opt_gui.builder.builder import *

from pyfemtet_opt_gui.models.analysis_model.analysis_model import get_am_model, FemprjModel
from pyfemtet_opt_gui.models.variables.var import get_var_model, VariableItemModel
from pyfemtet_opt_gui.models.config.config import get_config_model, ConfigItemModel
from pyfemtet_opt_gui.models.objectives.obj import get_obj_model, ObjectiveTableItemModel
from pyfemtet_opt_gui.models.constraints.model import get_cns_model, ConstraintModel
from pyfemtet_opt_gui.fem_interfaces import get_current_cad_name, CADIntegration
from pyfemtet_opt_gui.surrogate_model_interfaces import *

from pyfemtet_opt_gui.common.qt_util import *


class SurrogateCodeState(enum.Enum):
    normal = enum.auto()
    for_surrogate_training = enum.auto()
    for_surrogate_optimization = enum.auto()


def get_surrogate_code_state(use_surrogate) -> SurrogateCodeState:
    config_model: ConfigItemModel = get_config_model(None)
    surrogate_model_name: SurrogateModelNames = config_model.get_surrogate_model_name()

    if surrogate_model_name == SurrogateModelNames.no:
        if use_surrogate:
            assert False
        else:
            surrogate_code_state = SurrogateCodeState.normal
    else:
        if use_surrogate:
            surrogate_code_state = SurrogateCodeState.for_surrogate_optimization
        else:
            surrogate_code_state = SurrogateCodeState.for_surrogate_training

    return surrogate_code_state


def create_from_model(model, method='output_json', n_indent=1):
    code = ''

    commands_json = getattr(model, method)()
    commands = json.loads(commands_json)
    assert isinstance(commands, list | tuple)
    for command in commands:
        line = create_command_line(json.dumps(command), n_indent)
        code += line

    return code


def create_fem_script(surrogate_code_state: SurrogateCodeState):
    code = ''

    am_model: FemprjModel = get_am_model(None)
    (femprj_path, *related_paths), model_name = am_model.get_current_names()

    obj_model: ObjectiveTableItemModel = get_obj_model(None)
    parametric_output_indexes_use_as_objective = obj_model.output_dict()

    # construct FEM or surrogate interface
    if (
            surrogate_code_state == SurrogateCodeState.normal
            or surrogate_code_state == SurrogateCodeState.for_surrogate_training
    ):
        if get_current_cad_name() == CADIntegration.no:
            cmd_obj = dict(
                command='FemtetInterface',
                args=dict(
                    femprj_path=f'r"{femprj_path}"',
                    model_name=f'"{model_name}"',
                    parametric_output_indexes_use_as_objective=parametric_output_indexes_use_as_objective
                ),
                ret='fem',
            )

        elif get_current_cad_name() == CADIntegration.solidworks:

            sldprt_path = related_paths[0]

            cmd_obj = dict(
                command='FemtetWithSolidworksInterface',
                args=dict(
                    femprj_path=f'r"{femprj_path}"',
                    model_name=f'"{model_name}"',
                    sldprt_path=f'r"{sldprt_path}"',
                    parametric_output_indexes_use_as_objective=parametric_output_indexes_use_as_objective
                ),
                ret='fem',
            )

        else:
            raise NotImplementedError

    else:
        config_model: ConfigItemModel = get_config_model(None)
        surrogate_model_name = config_model.get_surrogate_model_name()
        assert surrogate_model_name != SurrogateModelNames.no
        assert training_history_path is not None

        v = Version(pyfemtet.__version__)
        if Version('0.9.5') <= v < Version('1.0.0'):
            print(parametric_output_indexes_use_as_objective)
            cmd_obj = dict(
                command=surrogate_model_name,
                args=dict(
                    history_path=f'"{training_history_path}"',
                    _output_directions=parametric_output_indexes_use_as_objective,
                ),
                ret='fem',
            )
            print(cmd_obj)

        else:
            assert False

    line = create_command_line(json.dumps(cmd_obj))
    code += line

    return code


def create_opt_script(surrogate_code_state: SurrogateCodeState):
    if surrogate_code_state == SurrogateCodeState.for_surrogate_training:
        model_: ConfigItemModel = get_config_model(None)
        model = model_.get_algorithm_model_for_training_surrogate_model()
    else:
        model_: ConfigItemModel = get_config_model(None)
        model = model_.algorithm_model
    return create_from_model(model)


def create_var_script():
    model: VariableItemModel = get_var_model(None)
    return create_from_model(model)


def create_cns_script():
    model: ConstraintModel = get_cns_model(None)
    return create_from_model(model)


def create_expr_cns_script():
    model: VariableItemModel = get_var_model(None)
    return create_from_model(model, 'output_expression_constraint_json')


def create_optimize_script():
    model: ConfigItemModel = get_config_model(None)
    return create_from_model(model)


def create_cns_function_def():
    model: ConstraintModel = get_cns_model(None)
    return create_from_model(model, method='output_funcdef_json', n_indent=0)


# for pyfemtet 0.x,
# femopt = FEMOpt(fem, opt, history_path)
def create_femopt(surrogate_code_state: SurrogateCodeState):
    model = get_config_model(None)
    code: str = create_from_model(model, 'output_femopt_json')

    if surrogate_code_state == SurrogateCodeState.for_surrogate_training:
        # history_path を参照する必要のある
        # ConfirmWizardPage の save_script などのために
        # 書き換えた history_path を保存
        # TODO: config_model で設定できるようにし、
        #   ここではそれを参照するだけにする
        model.history_path = training_history_path
        code = re.sub(
            r'history_path=".*?"',
            f'history_path="{training_history_path}"',
            code
        )

    return code


# 訓練データ作成時に決定する
# サロゲートモデルに読み込ませる用の
# 訓練データの履歴 csv path
# TODO: config_model で指定できるようにする
training_history_path: str | None = None


def create_script(
        path=None,
        *,
        use_surrogate: bool = False,
):
    """コード文字列を作成する。

    Args:
        path: コードの保存先。
        use_surrogate: サロゲートモデルの訓練データ作成用コードかどうか。

    """
    global training_history_path

    surrogate_code_state = get_surrogate_code_state(use_surrogate)

    if surrogate_code_state == SurrogateCodeState.for_surrogate_training:
        # 次にサロゲートモデル用スクリプトを作成する時に備えて
        # パスを設定する（作成しないなら単に使われない）
        if path is None:
            training_history_path = '訓練データ.csv'
        else:
            training_history_path = os.path.splitext(path)[0] + '_訓練データ.csv'

    code = ''
    code += create_message()
    code += '\n\n'
    code += create_header()
    code += '\n\n'
    if len(create_cns_function_def()) > 0:
        code += create_cns_function_def()
        code += '\n\n'
    code += create_main()
    code += '\n'
    code += create_fem_script(surrogate_code_state)
    code += '\n'
    code += create_opt_script(surrogate_code_state)
    code += '\n'
    code += create_femopt(surrogate_code_state)
    code += '\n'
    code += create_var_script()
    code += '\n'
    code += create_cns_script()
    code += '\n'
    code += create_expr_cns_script()
    code += '\n'
    code += create_optimize_script()
    code += '\n\n'
    code += create_footer()

    if path is not None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code)


def _test_create_surrogate_model():
    _start_debugging()

    # training
    create_script(path='_test.py')

    # surrogate
    create_script(path='_test_opt.py', use_surrogate=True)

    _end_debugging()


if __name__ == '__main__':
    _test_create_surrogate_model()
