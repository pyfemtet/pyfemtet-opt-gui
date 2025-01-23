import json
from pyfemtet_opt_gui_2.builder.builder import *

from pyfemtet_opt_gui_2.models.analysis_model.analysis_model import get_am_model, FemprjModel
from pyfemtet_opt_gui_2.models.variables.var import get_var_model, VariableItemModel
from pyfemtet_opt_gui_2.models.config.config import get_config_model, ConfigItemModel
from pyfemtet_opt_gui_2.models.objectives.obj import get_obj_model, ObjectiveTableItemModel


def create_from_model(model):
    commands_json = model.output_json()
    commands = json.loads(commands_json)
    assert isinstance(commands, list | tuple)
    for command in commands:
        line = create_command_line(json.dumps(command))
        print(line)


def create_fem_script():
    am_model: FemprjModel = get_am_model(None)
    femprj_path, model_name = am_model.get_current_names()

    obj_model: ObjectiveTableItemModel = get_obj_model(None)
    parametric_output_indexes_use_as_objective = obj_model.output_dict()


    cmd_obj = dict(
        command='FemtetInterface',
        args=dict(
            femprj_path=f'r"{femprj_path}"',
            model_name=f'"{model_name}"',
            parametric_output_indexes_use_as_objective=parametric_output_indexes_use_as_objective
        ),
        ret='fem',
    )

    line = create_command_line(json.dumps(cmd_obj))
    print(line)


def create_opt_script():
    model_: ConfigItemModel = get_config_model(None)
    model = model_.algorithm_model
    create_from_model(model)


def create_var_script():
    model: VariableItemModel = get_var_model(None)
    create_from_model(model)


def create_optimize_script():
    model: ConfigItemModel = get_config_model(None)
    create_from_model(model)


def create_script():
    print(create_header())
    print(create_main())
    create_fem_script()
    create_opt_script()
    print(create_femopt())
    create_var_script()
    create_optimize_script()
    # create_constraint_script()
    print(create_footer())


if __name__ == '__main__':
    create_script()
