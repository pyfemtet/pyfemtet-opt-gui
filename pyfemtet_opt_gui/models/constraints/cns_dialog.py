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

from pyfemtet_opt_gui.ui.ui_Dialog_cns_edit import Ui_Dialog

from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.common.return_msg import *
from pyfemtet_opt_gui.common.expression_processor import *

from pyfemtet_opt_gui.models.variables.var import get_var_model, VariableItemModelForTableView, VariableItemModel, VariableTableViewDelegate
from pyfemtet_opt_gui.models.constraints.model import get_cns_model, ConstraintModel, Constraint

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
        self.existing_constraint_name = existing_constraint_name

        self.setup_ui()
        self.setup_model()
        self.setup_view()
        self.setup_signal(load_femtet_fun)

    def setup_ui(self):
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

    def setup_model(self):
        # constraints
        self.constraints = get_cns_model(parent=self)

        # variables
        self.original_var_model = get_var_model(parent=self)
        self.var_model = VariableItemModelForTableView(self)
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

        # constraint
        if self.existing_constraint_name is not None:
            cns: Constraint = self.constraints.get_constraint(name=self.existing_constraint_name)

            self.ui.lineEdit_name.setText(cns.name)
            if cns.lb is not None:
                self.ui.lineEdit_lb.setText(str(cns.lb))
            if cns.ub is not None:
                self.ui.lineEdit_ub.setText(str(cns.ub))
            self.ui.plainTextEdit_cnsFormula.setPlainText(
                cns.expression
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
                'Max(,)'
            )
        )
        self.ui.pushButton_input_min.clicked.connect(
            lambda _: self.insert_text_to_expression(
                'Min(,)'
            )
        )
        self.ui.pushButton_input_mean.clicked.connect(
            lambda _: self.insert_text_to_expression(
                'Mean(,)'
            )
        )

    def update_evaluated_value(self, expression: str):

        label = self.ui.label_calc_value

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
                raise ExpressionParseError(expr)

            # no error
            value = ret[expr_key]

            # set default style
            palette = label.palette()
            default_color = label.style().standardPalette().color(QPalette.ColorRole.WindowText)
            palette.setColor(QPalette.ColorRole.WindowText, default_color)
            label.setPalette(palette)
            font = label.font()
            font.setBold(False)
            label.setFont(font)

        except ExpressionParseError:
            value = '計算エラー'

            # set 赤字・太字
            palette = label.palette()
            palette.setColor(QPalette.ColorRole.WindowText, QColor("red"))
            label.setPalette(palette)
            font = label.font()
            font.setBold(True)
            label.setFont(font)

        self.ui.label_calc_value.setText(
            '現在の計算値: ' + str(value)
        )

    def get_selected_variable(self) -> str | None:

        index: QModelIndex = self.ui.tableView_prmsOnCns.currentIndex()

        # no current index, do nothing
        if not index.isValid():
            return None

        # get source model

        # noinspection PyTypeChecker
        proxy_model = index.model()
        assert isinstance(proxy_model, type(self.var_model))
        proxy_model: VariableItemModelForTableView

        # noinspection PyTypeChecker
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

        # 上下限の設定がされているかどうか
        with nullcontext():
            lb = self.ui.lineEdit_lb.text()
            if lb != '':
                try:
                    lb_value = float(lb)
                except ValueError:
                    show_return_msg(ReturnMsg.Error.not_a_pure_number, parent=self.parent(), additional_message=': ' + lb)
                    return None
            else:
                lb_value = None

            ub = self.ui.lineEdit_ub.text()
            if ub != '':
                try:
                    ub_value = float(ub)
                except ValueError:
                    show_return_msg(ReturnMsg.Error.not_a_pure_number, parent=self.parent(), additional_message=': ' + ub)
                    return None
            else:
                ub_value = None

        # Constraint オブジェクトを初期化
        with nullcontext():
            constraint: Constraint = Constraint(self.original_var_model)
            constraint.name = self.ui.lineEdit_name.text() if self.ui.lineEdit_name.text() != '' else self.constraints.get_unique_name()
            constraint.expression = self.ui.plainTextEdit_cnsFormula.toPlainText()
            constraint.lb = lb_value
            constraint.ub = ub_value

        # 拘束式の設定として正しいかどうかを判定
        ret_msg, a_msg = constraint.finalize_check()

        # 正しくなければ or 危ういならばダイアログを表示
        # して処理を続行するかどうかを分岐
        if not can_continue(
                return_msg=ret_msg,
                parent=self.parent(),
                additional_message=a_msg,
        ):
            return None

        # 1. 「編集」からダイアログに来ているが、
        # 2. name が変更されており、
        # 3. かつ新しい name が既存の ConstraintModel に
        # 含まれる場合、名前が重複していますエラー
        if self.existing_constraint_name is not None:  # 1.
            if self.existing_constraint_name != constraint.name:  # 2.
                if constraint.name in self.constraints.get_constraint_names():  # 3.
                    can_continue(
                        ReturnMsg.Error.duplicated_constraint_name,
                        parent=self.parent(),
                        additional_message=f'拘束式名: {constraint.name}',
                    )
                    return None

        # ConstraintModel モデルに書き戻す
        self.constraints.set_constraint(constraint, self.existing_constraint_name)

        super().accept()

    def _load_femtet_debug(self):

        # noinspection PyTypeChecker
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
