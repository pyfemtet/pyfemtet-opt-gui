# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

from pyfemtet_opt_gui_2.ui.ui_Dialog_cns_edit import Ui_Dialog

from pyfemtet_opt_gui_2.common.qt_util import *
from pyfemtet_opt_gui_2.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui_2.common.return_msg import *
from pyfemtet_opt_gui_2.common.expression_processor import *
from pyfemtet_opt_gui_2.femtet.femtet import *

from pyfemtet_opt_gui_2.models.variables.var import get_var_model, VariableItemModelForTableView, VariableItemModel, VariableTableViewDelegate
from pyfemtet_opt_gui_2.models.constraints.model import get_cns_model, ConstraintModel, Constraint


import enum
import sys
from contextlib import nullcontext


class ConstraintEditorDialog(QDialog):
    ui: Ui_Dialog
    var_model: VariableItemModelForTableView
    original_var_model: VariableItemModel
    column_resizer: ResizeColumn

    constraints: ConstraintModel

    def __init__(
            self,
            parent=None,
            f=Qt.WindowType.Dialog,
            load_femtet_fun: callable = None,
            existing_constraint_name: str = None
    ):
        super().__init__(parent, f)

        self.setup_ui()
        self.setup_model(existing_constraint_name)
        self.setup_view()
        self.setup_signal(load_femtet_fun)

    def setup_ui(self):
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def setup_model(self, existing_constraint_name):
        # constraints
        self.constraints = get_cns_model(parent=self)

        # constraint
        if existing_constraint_name is not None:
            raise NotImplementedError

        # variables
        self.original_var_model = get_var_model(parent=self, _with_dummy=True)
        self.var_model = VariableItemModelForTableView()
        self.var_model.setSourceModel(self.original_var_model)

    def setup_view(self):
        view = self.ui.tableView_prmsOnCns
        view.setModel(self.var_model)
        # view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        view.setItemDelegate(VariableTableViewDelegate())
        self.column_resizer = ResizeColumn(view)
        self.column_resizer.resize_all_columns()

        editor = self.ui.plainTextEdit_cnsFormula
        editor.textChanged.connect(
            lambda: self.update_evaluated_value(editor.toPlainText())
        )

    def setup_signal(self, load_femtet_fun: callable):

        # load femtet
        if load_femtet_fun is not None:
            self.ui.pushButton_load_var.clicked.connect(
                lambda *_: load_femtet_fun()
            )
        else:
            self.ui.pushButton_load_var.clicked.connect(
                lambda *_: self._load_femtet_debug()
            )

        # 「選択中の変数を入力」
        self.ui.pushButton_input_var.clicked.connect(
            lambda _: self.insert_text_to_expression(
                self.get_selected_variable()
            )
        )

        # 記号
        self.ui.pushButton_input_plus.clicked.connect(
            lambda _: self.insert_text_to_expression(
                '+'
            )
        )
        self.ui.pushButton_input_minus.clicked.connect(
            lambda _: self.insert_text_to_expression(
                '-'
            )
        )
        self.ui.pushButton_input_devide.clicked.connect(
            lambda _: self.insert_text_to_expression(
                '/'
            )
        )
        self.ui.pushButton_input_multiply.clicked.connect(
            lambda _: self.insert_text_to_expression(
                '*'
            )
        )
        self.ui.pushButton_input_comma.clicked.connect(
            lambda _: self.insert_text_to_expression(
                ', '
            )
        )

        # 関数
        self.ui.pushButton_input_max.clicked.connect(
            lambda _: self.insert_text_to_expression(
                'max(,)'
            )
        )
        self.ui.pushButton_input_min.clicked.connect(
            lambda _: self.insert_text_to_expression(
                'min(,)'
            )
        )
        self.ui.pushButton_input_mean.clicked.connect(
            lambda _: self.insert_text_to_expression(
                'mean(,)'
            )
        )

    def update_evaluated_value(self, expression: str):
        try:
            # error check
            expr = Expression(expression)

            # eval
            expr_key = 'this_is_a_current_expression_key'
            expressions = self.original_var_model.get_current_variables()
            expressions.update(
                {expr_key: expr}
            )
            ret, r_msg, _ = eval_expressions(expressions)
            if r_msg != ReturnMsg.no_message:
                raise SympifyError(expr)

            # no error
            value = ret[expr_key]

        except SympifyError:
            value = '計算エラー'

        self.ui.label_calc_value.setText(
            '現在の計算値: ' + str(value)
        )

    def get_selected_variable(self) -> str | None:
        indexes: list[QModelIndex] = self.ui.tableView_prmsOnCns.selectedIndexes()

        # no index, do nothing
        if len(indexes) == 0:
            return None

        # process 1st index only
        index: QModelIndex = indexes[0]

        # get source model
        proxy_model = index.model()
        assert isinstance(proxy_model, type(self.var_model))
        proxy_model: VariableItemModelForTableView
        model = proxy_model.sourceModel()
        assert isinstance(model, VariableItemModel)
        model: VariableItemModel

        # get name
        r = proxy_model.mapToSource(index).row()
        c = get_column_by_header_data(model, model.ColumnNames.name)
        item = model.item(r, c)
        name = item.text()

        return name

    def insert_text_to_expression(self, text):
        if text is not None:
            editor = self.ui.plainTextEdit_cnsFormula
            if '()' in text:
                assert len(text.split('()')) == 2
                text_cursor = editor.textCursor()
                pre, post = text.split('()')

                current = editor.textCursor().selectedText()

                text_cursor.removeSelectedText()
                text_cursor.insertText(
                    pre + '( ' + current + ' )' + post
                )

            elif '(,)' in text:
                assert len(text.split('(,)')) == 2
                text_cursor = editor.textCursor()
                pre, post = text.split('(,)')

                current = editor.textCursor().selectedText()
                arr = current.split(',')

                if len(arr) == 1:
                    new_text = f'{pre}( {arr[0]}, ){post}'

                else:
                    new_text = pre + '( ' + ', '.join(arr) + ' )' + post

                text_cursor.removeSelectedText()
                text_cursor.insertText(new_text)

            else:
                cursor = editor.textCursor()
                cursor.insertText(' ' + text + ' ')

    def accept(self):
        # ret_msg, a_msg = ReturnMsg.Error._test, ''
        # ret_msg, a_msg = ReturnMsg.Warn._test, ''

        constraint: Constraint = Constraint(self.original_var_model)
        constraint.name = self.ui.lineEdit_name.text() if self.ui.lineEdit_name.text() != '' else self.constraints.get_unique_name()
        constraint.expression = self.ui.plainTextEdit_cnsFormula.toPlainText()
        constraint.lb = float(self.ui.lineEdit_lb.text()) if self.ui.lineEdit_lb.text() != '' else None
        constraint.ub = float(self.ui.lineEdit_ub.text()) if self.ui.lineEdit_ub.text() != '' else None

        ret_msg, a_msg = constraint.finalize_check()

        if not can_continue(
            return_msg=ret_msg,
            parent=self,
            with_cancel_button='auto',
            additional_message=a_msg,
            no_dialog_if_info=False,
        ):
            return None

        self.constraints.set_constraint(constraint)

        super().accept()

    def _load_femtet_debug(self):
        from pyfemtet_opt_gui_2.models.variables.var import VariableItemModel
        source_model = self.var_model.sourceModel()
        assert isinstance(source_model, VariableItemModel)
        source_model: VariableItemModel
        source_model.load_femtet()


if __name__ == '__main__':
    app = QApplication()
    app.setStyle('fusion')
    window = ConstraintEditorDialog()
    window.show()
    app.exec()
