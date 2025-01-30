import json
from pyfemtet_opt_gui.builder.builder import *

from pyfemtet_opt_gui.models.analysis_model.analysis_model import get_am_model, FemprjModel
from pyfemtet_opt_gui.models.variables.var import get_var_model, VariableItemModel
from pyfemtet_opt_gui.models.config.config import get_config_model, ConfigItemModel
from pyfemtet_opt_gui.models.objectives.obj import get_obj_model, ObjectiveTableItemModel
from pyfemtet_opt_gui.models.constraints.model import get_cns_model, ConstraintModel


def create_from_model(model, method='output_json', n_indent=1):
    code = ''

    commands_json = getattr(model, method)()
    commands = json.loads(commands_json)
    assert isinstance(commands, list | tuple)
    for command in commands:
        line = create_command_line(json.dumps(command), n_indent)
        code += line

    return code


def create_fem_script():
    code = ''

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
    code += line

    return code


def create_opt_script():
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


# femopt = FEMOpt(fem, opt, history_path)
def create_femopt(n_indent=1):
    model = get_config_model(None)
    code = create_from_model(model, 'output_femopt_json')
    return code


def create_script(path=None):
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
    code += create_fem_script()
    code += '\n'
    code += create_opt_script()
    code += '\n'
    code += create_femopt()
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


if __name__ == '__main__':
    create_script()
