import json
from pyfemtet_opt_gui_2.builder.builder import *

from pyfemtet_opt_gui_2.models.analysis_model.analysis_model import get_am_model, FemprjModel
from pyfemtet_opt_gui_2.models.variables.var import get_var_model, VariableItemModel


def create_fem_script():
    am_model: FemprjModel = get_am_model(None)
    femprj_path, model_name = am_model.get_current_names()

    cmd_obj = dict(
        command='FemtetInterface',
        args=dict(
            femprj_path=f'"{femprj_path}"',
            model_name=f'"{model_name}"',
        ),
        ret='fem',
    )

    line = create_command_line(json.dumps(cmd_obj))
    print(line)


def create_var_script():
    var_model: VariableItemModel = get_var_model(None)
    commands_json = var_model.output_json()
    commands = json.loads(commands_json)
    assert isinstance(commands, list | tuple)

    for command in commands:
        line = create_command_line(json.dumps(command))

        print(line)


def create_script():
    create_fem_script()
    create_var_script()



if __name__ == '__main__':
    create_script()