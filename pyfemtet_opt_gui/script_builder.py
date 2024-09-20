from PySide6.QtCore import Qt

from pyfemtet_opt_gui.problem_model import ProblemItemModel
from pyfemtet_opt_gui.item_as_model import MyStandardItemAsTableModel
from pyfemtet_opt_gui.prm_model import PrmModel
from pyfemtet_opt_gui.cns_model import CnsModel
from pyfemtet_opt_gui.expression_eval import extract_variables


def get_header(cns_model: CnsModel):
    code = f'''from statistics import mean
from pyfemtet.opt import FemtetInterface, OptunaOptimizer, FEMOpt
{get_constraint(cns_model)}

def main():'''
    return code


def get_femopt(femprj_model: MyStandardItemAsTableModel, obj_model: MyStandardItemAsTableModel):

    femprj_path = femprj_model.get_item(0, 2).text()
    model_name = femprj_model.get_item(1, 2).text()

    code = f'''
    # settings to open femtet and objectives
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
            d_col = obj_model.get_col_from_name('  direction  ')
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


def get_constraint(cns_model: CnsModel):
    code = ''

    counter = 0

    for row in range(cns_model.rowCount()):
        use_col = cns_model.get_col_from_name(cns_model.USE)
        use = cns_model.get_item(row, use_col).checkState()
        if use == Qt.CheckState.Checked:  # uncheckable row (i.e. header) must be False
            # get formula
            col = cns_model.get_col_from_name(cns_model.FORMULA)
            item = cns_model.get_item(row, col)
            formula = item.text()

            # format formula
            formula = formula.replace('\n', '')

            # get Name nodes from ast
            variables: set = extract_variables(formula)

            # create code snippet
            counter += 1
            code += f'''

def constraint_{counter}(Femtet):'''

            for var in variables:
                code += f'''
    {var} = Femtet.GetVariableValue("{var}")'''

            code += f'''
    return {formula}
'''

    return code


def get_add_parameter(prm_model: PrmModel):
    code = '''
    # parameter setting'''

    for row in range(prm_model.rowCount()):
        use_col = prm_model.get_col_from_name(prm_model.USE)
        use = prm_model.get_item(row, use_col).checkState()
        if use == Qt.CheckState.Checked:  # uncheckable row (i.e. header) must be False
            name_col = prm_model.get_col_from_name(prm_model.NAME)
            init_col = prm_model.get_col_from_name(prm_model.INIT)
            lb_col = prm_model.get_col_from_name(prm_model.LB)
            ub_col = prm_model.get_col_from_name(prm_model.UB)
            name = prm_model.get_item(row, name_col).text()
            init = prm_model.get_item(row, init_col).text()
            lb = prm_model.get_item(row, lb_col).text()
            ub = prm_model.get_item(row, ub_col).text()

            code += f'''
    femopt.add_parameter("{name}", {init}, {lb}, {ub})'''

    return code


def get_add_constraint(cns_model: CnsModel):
    code = '''
    
    # constraints setting'''

    counter = 0

    for row in range(cns_model.rowCount()):
        use_col = cns_model.get_col_from_name(cns_model.USE)
        use = cns_model.get_item(row, use_col).checkState()

        if use == Qt.CheckState.Checked:  # uncheckable row (i.e. header) must be False
            # get name
            col = cns_model.get_col_from_name(cns_model.NAME)
            item = cns_model.get_item(row, col)

            if item.text() == cns_model.AUTOMATIC_CNS_NAME:
                name = None
            elif not item.text():
                name = None
            else:
                name = f'"{item.text()}"'

            # get function
            counter += 1
            func_name: str = f'constraint_{counter}'

            # get lb
            col = cns_model.get_col_from_name(cns_model.LB)
            item = cns_model.get_item(row, col)
            lb: str = item.text() if item.text() else 'None'

            # get ub
            col = cns_model.get_col_from_name(cns_model.UB)
            item = cns_model.get_item(row, col)
            ub: str = item.text() if item.text() else 'None'

            # get strict
            col = cns_model.get_col_from_name(cns_model.STRICT)
            item = cns_model.get_item(row, col)
            strict: str = 'True' if item.checkState() == Qt.CheckState.Checked else 'False'

            # create code
            code += f'''
    femopt.add_constraint(
        fun={func_name},
        name={name},
        lower_bound={lb},
        upper_bound={ub},
        strict={strict},
    )'''
    return code


def get_optimize(run_model: MyStandardItemAsTableModel):
    code = '''
    
    # run optimization
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
    )'''
    return code


def get_entry_point():
    code = f'''


if __name__ == '__main__':
    main()
'''
    return code


def build_script_main(model: ProblemItemModel, path: str, with_run=False):
    code = ''

    code += get_header(model.cns_model)
    code += get_femopt(model.femprj_model, model.obj_model)
    code += get_add_parameter(model.prm_model)
    code += get_add_constraint(model.cns_model)
    code += get_optimize(model.run_model)
    code += get_entry_point()

    print(code)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)

    if with_run:
        # Femtet との接続は一度に一プロセスで、
        # 現在のプロセスが解放されない限り新しい
        # Femtet が必要なので現在のプロセスで実行する

        # 以下の方法は PyFemtet 内でファイルが存在する
        # ことを前提に inspect などで処理する機能が
        # 動作しないので実装してはいけない
        # exec(code)

        import os
        import sys
        there, it = os.path.split(path)
        module_name = os.path.splitext(it)[0]
        os.chdir(there)  # csv 保存ディレクトリを分かりやすくするためカレントディレクトリを変更
        sys.path.append(there)
        exec(f'from {module_name} import *; main()')

