from PySide6.QtWidgets import QDialog, QHeaderView

from pyfemtet_opt_gui.ui.ui_cns_input import Ui_Dialog
from pyfemtet_opt_gui.ui.return_code import ReturnCode, should_stop

from pyfemtet_opt_gui.prm_model import PrmModel
from pyfemtet_opt_gui.cns_model import CnsModel

from pyfemtet_opt_gui.expression_eval import create_formula, ExpressionEvalError

import pyfemtet_opt_gui._p as _p  # must be same folder and cannot import via `from` keyword.


class ConstraintInputDialog(QDialog):

    def __init__(
            self,
            parent=...,
            f=...,
            target_cns_row: int = None,  # if None, add new line when accepted
    ):
        super().__init__(parent, f)

        # set modality
        self.setModal(True)

        # setup ui
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # detail setup ui
        self.ui.tableView_prmsOnCns.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # register parent as wizard
        from pyfemtet_opt_gui.main import MainWizard
        self.wizard: MainWizard = parent

        # sync parameters
        self.update_problem()

        # set prm_model and cns_model
        self.prm_model: PrmModel = self.wizard._problem.prm_model
        self.cns_model: CnsModel = self.wizard._problem.cns_model

        # set parameter (proxy) model to tableview
        from pyfemtet_opt_gui.cns_model import PrmProxyModelForCns
        prm_proxy_model = PrmProxyModelForCns()
        prm_proxy_model.setSourceModel(self.prm_model)
        self.ui.tableView_prmsOnCns.setModel(prm_proxy_model)

        # set target
        self.target_cns_row = target_cns_row

        # set default values
        if self.target_cns_row is None:
            self.ui.lineEdit_lb.setText('0')

        # if edit mode, set table values
        else:
            # get
            lb = self.cns_model.get_item(self.target_cns_row, self.cns_model.get_col_from_name(self.cns_model.LB)).text()
            ub = self.cns_model.get_item(self.target_cns_row, self.cns_model.get_col_from_name(self.cns_model.UB)).text()
            formula = self.cns_model.get_item(self.target_cns_row, self.cns_model.get_col_from_name(self.cns_model.FORMULA)).text()
            name = self.cns_model.get_item(self.target_cns_row, self.cns_model.get_col_from_name(self.cns_model.NAME)).text()

            # set
            self.ui.lineEdit_lb.setText(str(lb))
            self.ui.lineEdit_ub.setText(str(ub))
            self.ui.plainTextEdit_cnsFormula.setPlainText(str(formula))
            self.ui.lineEdit_name.setText(str(name))

    # register constraint
    def accept(self):

        # if error, inhibit accept
        if not self.check_cns_expression():  # should_stop inside
            return

        # if error, inhibit accept
        if not self.check_boundary():  # should_stop inside
            return

        # add new row to table if needed
        if self.target_cns_row is None:
            self.cns_model.add_row()
            self.target_cns_row = self.cns_model.get_n_rows() - 1

        # register constraint information to accept
        self.cns_model.set_constraint_data(
            row=self.target_cns_row,
            name=self.ui.lineEdit_name.text() or self.cns_model.AUTOMATIC_CNS_NAME,
            lb=self.ui.lineEdit_lb.text(),
            ub=self.ui.lineEdit_ub.text(),
            formula=self.ui.plainTextEdit_cnsFormula.toPlainText(),
            strict=True,
        )

        # done
        super().accept()

    def update_problem(self):
        self.wizard.update_problem()
        self.load_prm()

    def load_prm(self) -> ReturnCode:
        # モデルの再読み込み
        ret_code = self.wizard._problem.prm_model.load()

        # cns ページの中で使う prm tableView に設定
        from pyfemtet_opt_gui.cns_model import PrmProxyModelForCns
        model = self.wizard._problem.prm_model
        proxy_model_for_cns = PrmProxyModelForCns(model)
        proxy_model_for_cns.setSourceModel(model)
        self.ui.tableView_prmsOnCns.setModel(proxy_model_for_cns)

        return ret_code

    def check_cns_expression(self) -> bool:

        # check syntax error
        expression = self.ui.plainTextEdit_cnsFormula.toPlainText()
        try:
            fun = create_formula(
                expression,
                self.prm_model.get_variable_names(),
            )

        # invalid syntax
        except SyntaxError as e:
            should_stop(ReturnCode.ERROR.SYNTAX_ERROR_CNS_FORMULA, parent=self)
            return False

        # undefined variable, function or operator
        except ExpressionEvalError as e:
            should_stop(ReturnCode.ERROR.UNDEFINED_FORMULA_NODE)
            return False

        return True

    def check_boundary(self) -> bool:
        str_lb = self.ui.lineEdit_lb.text()
        str_ub = self.ui.lineEdit_ub.text()

        # convert input to float or None
        if str_lb:
            try:
                lb_float = float(str_lb)
            except Exception:
                should_stop(ReturnCode.ERROR.NOT_FLOAT, parent=self)
                return False
        else:
            lb_float = None

        # convert input to float or None
        if str_ub:
            try:
                ub_float = float(str_ub)
            except Exception:
                should_stop(ReturnCode.ERROR.NOT_FLOAT, parent=self)
                return False
        else:
            ub_float = None

        # re-declare
        lb_float: float or None
        ub_float: float or None

        # check boundary
        if lb_float is None and ub_float is None:
            should_stop(ReturnCode.ERROR.BOUND_EMPTY)
            return False

        elif lb_float is not None and ub_float is not None:
            if lb_float == ub_float:
                should_stop(ReturnCode.ERROR.BOUND_NO_RANGE)
                return False

            elif lb_float > ub_float:
                should_stop(ReturnCode.ERROR.BOUND_LB_OVER_UB)
                return False

        return True

    def add_prm_to_cns_formula(self):
        # get selection
        selected_proxy_indexes = self.ui.tableView_prmsOnCns.selectedIndexes()
        """proxy indexes of selected cells"""

        if selected_proxy_indexes:
            # get source model
            from pyfemtet_opt_gui.cns_model import PrmProxyModelForCns
            proxy_model: PrmProxyModelForCns = self.ui.tableView_prmsOnCns.model()
            prm_model: PrmModel = proxy_model.sourceModel()

            # get source index
            proxy_index = selected_proxy_indexes[0]
            source_index = proxy_model.mapToSource(proxy_index)

            # get name column index
            name_col = prm_model.get_col_from_name(prm_model.NAME)

            # get name item
            item = prm_model.get_item(source_index.row(), name_col)

            # get name
            name = item.text()

            # transfer it to text input
            cursor = self.ui.plainTextEdit_cnsFormula.textCursor()
            cursor.insertText(name)

        # else:
        #     should_stop(ReturnCode.WARNING.PARAMETER_NOT_SELECTED_1)

    def add_max_to_cns_formula(self):
        # transfer it to text input
        cursor = self.ui.plainTextEdit_cnsFormula.textCursor()
        cursor.insertText('max(  )')

    def add_min_to_cns_formula(self):
        # transfer it to text input
        cursor = self.ui.plainTextEdit_cnsFormula.textCursor()
        cursor.insertText('min(  )')

    def add_mean_to_cns_formula(self):
        # transfer it to text input
        cursor = self.ui.plainTextEdit_cnsFormula.textCursor()
        cursor.insertText('mean(  )')

