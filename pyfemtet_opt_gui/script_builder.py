from PySide6.QtCore import Qt

from pyfemtet_opt_gui.problem_model import ProblemItemModel
from pyfemtet_opt_gui.item_as_model import MyStandardItemAsTableModel


def get_header():
    code = f'''
from pyfemtet.opt import FemtetInterface, OptunaOptimizer, FEMOpt


def main():
'''
    return code


def get_femopt(femprj_model: MyStandardItemAsTableModel, obj_model: MyStandardItemAsTableModel):

    femprj_path = femprj_model.get_item(0, 2).text()
    model_name = femprj_model.get_item(1, 2).text()

    code = f'''
    femprj_path = r"{femprj_path}"
    model_name = "{model_name}"
    fem = FemtetInterface(
        femprj_path=femprj_path,
        model_name=model_name,
        parametric_output_indexes_use_as_objective={{'''

    for row in range(1, obj_model.rowCount()):  # exclude header row

        idx = row - 1  # because of the header row existing, objective index = row - 1.

        use_col = obj_model.get_col_from_name('use')
        checked = obj_model.get_item(row, use_col).checkState()
        if checked == Qt.CheckState.Checked:
            d_col = obj_model.get_col_from_name('direction')
            direction = obj_model.get_item(row, d_col).text()
            if direction == 'Set to...':
                st_col = obj_model.get_col_from_name('set to')
                direction = obj_model.get_item(row, st_col).text()
            else:
                direction = f'"{direction}"'

            code += f'''
            {idx}: {direction},'''  # dict[[int], str or float]

    code += f'''
        }},
    )

    femopt = FEMOpt(fem=fem)
'''
    return code


def get_add_parameter(prm_model: MyStandardItemAsTableModel):
    code = ''

    for row in range(prm_model.rowCount()):
        use_col = prm_model.get_col_from_name('use')
        use = prm_model.get_item(row, use_col).checkState()
        if use == Qt.CheckState.Checked:  # uncheckable row (i.e. header) must be False
            name_col = prm_model.get_col_from_name('name')
            init_col = prm_model.get_col_from_name('expression')
            lb_col = prm_model.get_col_from_name('lb')
            ub_col = prm_model.get_col_from_name('ub')
            name = prm_model.get_item(row, name_col).text()
            init = prm_model.get_item(row, init_col).text()
            lb = prm_model.get_item(row, lb_col).text()
            ub = prm_model.get_item(row, ub_col).text()

            code += f'''
    femopt.add_parameter("{name}", {init}, {lb}, {ub})'''

    return code


def get_optimize(run_model: MyStandardItemAsTableModel):
    code = '''
    femopt.optimize('''

    for row in range(1, run_model.rowCount()):  # exclude header row

        use_col = run_model.get_col_from_name('use')
        use_item = run_model.get_item(row, use_col)

        if use_item.isCheckable():
            if use_item.checkState() == Qt.CheckState.Checked:
                arg_name = run_model.get_item(row, 1).text()
                arg_value = run_model.get_item(row, 2).text()
                if arg_name == 'timeout':
                    arg_value = str(float(arg_value) * 60)
                code += f'''
        {arg_name}={arg_value},'''

        else:
            arg_name = run_model.get_item(row, 1).text()
            arg_value = run_model.get_item(row, 2).text()
            code += f'''
        {arg_name}={arg_value},'''
    code += '''
    )
    femopt.terminate_all()
'''
    return code


def get_entry_point():
    code = f'''
if __name__ == '__main__':
    main()
'''
    return code


def build_script_main(model: ProblemItemModel, path: str, with_run=False):
    code = ''

    code += get_header()
    code += get_femopt(model.femprj_model, model.obj_model)
    code += get_add_parameter(model.prm_model)
    code += get_optimize(model.run_model)
    code += get_entry_point()

    print(code)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

    if with_run:
        import os
        import sys
        there, it = os.path.split(path)
        module_name = os.path.splitext(it)[0]
        os.chdir(there)
        sys.path.append(there)
        exec(f'import {module_name}; {module_name}.main()')



