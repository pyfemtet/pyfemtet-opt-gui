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


import enum
import sys
from contextlib import nullcontext

from pyfemtet_opt_gui_2.ui.ui_WizardPage_var import Ui_WizardPage

from pyfemtet_opt_gui_2.common.qt_util import *
from pyfemtet_opt_gui_2.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui_2.common.return_msg import *
from pyfemtet_opt_gui_2.common.expression_processor import *
from pyfemtet_opt_gui_2.femtet.femtet import *


# ===== model =====
_VAR_MODEL = None
_WITH_DUMMY = False


def get_var_model(parent, _with_dummy=None) -> 'VariableItemModel':
    global _VAR_MODEL
    if _VAR_MODEL is None:
        assert parent is not None
        _VAR_MODEL = VariableItemModel(
            parent,
            _WITH_DUMMY if _with_dummy is None else _with_dummy,
        )
    return _VAR_MODEL


def get_var_model_for_problem(parent, _with_dummy=None):
    var_model = get_var_model(parent, _with_dummy)
    var_model_for_problem = QVariableItemModelForProblem()
    var_model_for_problem.setSourceModel(var_model)
    return var_model_for_problem


# ===== constants =====
class VariableColumnNames(enum.StrEnum):
    use = CommonItemColumnName.use
    name = '変数名'
    initial_value = '初期値 または\n文字式'
    lower_bound = '下限'
    upper_bound = '上限'
    test_value = 'テスト値 または\n文字式の計算結果'
    note = '備考'


# ===== qt objects =====
# 個別ページに表示される TableView の Delegate
class VariableTableViewDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        header_data = get_internal_header_data(index)
        if (
                header_data == VariableColumnNames.initial_value
                or header_data == VariableColumnNames.lower_bound
                or header_data == VariableColumnNames.upper_bound
        ):
            editor: QLineEdit = super().createEditor(parent, option, index)
            return editor

        else:
            return super().createEditor(parent, option, index)

    def setModelData(self, editor, model, index):
        header_data = get_internal_header_data(index)

        if (
                header_data == VariableColumnNames.initial_value
                or header_data == VariableColumnNames.lower_bound
                or header_data == VariableColumnNames.upper_bound
        ):
            editor: QLineEdit

            def get_value(header_data_) -> float:
                c_ = get_column_by_header_data(model, header_data_)
                index_ = model.index(index.row(), c_)
                data_: Expression = model.data(index_, Qt.ItemDataRole.UserRole)
                return data_.value

            # get current value
            init: float = get_value(VariableColumnNames.initial_value)
            lb: float = get_value(VariableColumnNames.lower_bound)
            ub: float = get_value(VariableColumnNames.upper_bound)

            # Validate to be an expression
            text = editor.text()
            try:
                new_expression: Expression = Expression(text)

            # Not a valid expression
            except Exception:
                ret_msg = ReturnMsg.Error.cannot_recognize_as_an_expression
                if not can_continue(ret_msg, parent=self.parent(), additional_message=text):
                    return
                else:
                    raise RuntimeError('Internal Error!')

            # Valid expression but not a number
            if not new_expression.is_number():
                ret_msg = ReturnMsg.Error.not_a_number
                if not can_continue(ret_msg, parent=self.parent(), additional_message=text):
                    return
                else:
                    raise RuntimeError('Internal Error!')

            # overwrite it with the new user-input
            if header_data == VariableColumnNames.initial_value:
                init = new_expression.value

            elif header_data == VariableColumnNames.lower_bound:
                lb = new_expression.value

            elif header_data == VariableColumnNames.upper_bound:
                ub = new_expression.value

            else:
                raise NotImplementedError

            ret_msg, error_numbers = check_bounds(init, lb, ub)
            if not can_continue(ret_msg, parent=self.parent(), additional_message=error_numbers):
                return

            else:
                with EditModel(model):
                    model.setData(index, text, Qt.ItemDataRole.DisplayRole)
                    model.setData(index, new_expression, Qt.ItemDataRole.UserRole)

        else:
            super().setModelData(editor, model, index)


# 大元の ItemModel
class VariableItemModel(StandardItemModelWithHeader):

    ColumnNames = VariableColumnNames

    def load_femtet(self):
        # variables 取得
        expression: Expression
        expressions: dict[str, Expression]
        expressions, ret_msg = get_variables()
        if not can_continue(ret_msg, self.parent()):
            return

        # variables の評価
        # Femtet から取得してもよいが、
        # initial_value が stash されたものを
        # 使う仕様に変える可能性があるため
        variable_values, ret_msg = eval_expressions(expressions)
        if not can_continue(ret_msg, self.parent()):
            return

        # 現在の状態を stash
        stashed_data: dict[str, dict[str, str]] = self.stash_current_table()

        rows = len(expressions) + 1
        with EditModel(self):
            self.setRowCount(rows)  # header row for treeview

            for r, (name, expression) in zip(range(1, rows), expressions.items()):
                # ===== use =====
                with nullcontext():  # editor で畳みやすくするためだけのコンテキストマネージャ
                    item = QStandardItem()
                    if expression.is_number():
                        # expression が float なら checkable
                        item.setCheckable(True)
                        if name in stashed_data.keys():
                            self.set_data_from_stash(item, name, self.ColumnNames.use, stashed_data)
                        else:
                            item.setCheckState(Qt.CheckState.Checked)
                    else:
                        # disabled は行全体に適用するので flags() で定義
                        pass
                    c = self.get_column_by_header_data(self.ColumnNames.use)
                    item.setEditable(False)
                    self.setItem(r, c, item)

                # ===== name =====
                with nullcontext():
                    c = self.get_column_by_header_data(self.ColumnNames.name)
                    item = QStandardItem()
                    item.setText(name)
                    item.setEditable(False)
                    self.setItem(r, c, item)

                # ===== initial =====
                with nullcontext():
                    # これは Femtet の値を優先して stash から更新しない
                    c = self.get_column_by_header_data(self.ColumnNames.initial_value)
                    item = QStandardItem()
                    item.setText(expression.expr)
                    item.setData(expression, Qt.ItemDataRole.UserRole)
                    self.setItem(r, c, item)

                # ===== lb =====
                with nullcontext():
                    item = QStandardItem()
                    # 新しい変数の式が文字式ならとにかく空欄にする
                    if expression.is_expression():
                        display_value = ''
                        item.setText(display_value)

                    # 新しい変数が数値であって、
                    else:
                        # 以前からある変数であって、
                        if name in stashed_data.keys():
                            self.set_data_from_stash(item, name, self.ColumnNames.lower_bound, stashed_data)
                            # 以前は文字式であって空欄が入っていた場合
                            if item.text() == '':
                                # 上の set_data_from_stash を破棄して
                                item = QStandardItem()
                                # デフォルト値を計算して設定する
                                tmp_expression = Expression('0.9 * ' + expression.expr)
                                item.setData(tmp_expression, Qt.ItemDataRole.UserRole)
                                display_value = tmp_expression.expr
                                item.setText(display_value)
                            # 以前から何か数値が入っていた場合
                            else:
                                # 上下限チェックを満たしていれば
                                assert expression.is_number()
                                stashed: Expression = item.data(Qt.ItemDataRole.UserRole)
                                ret_msg, error_nums = check_bounds(expression.value, lb=stashed.value)
                                if ret_msg == ReturnMsg.no_message:
                                    # stash_data をそのまま使う
                                    pass

                                # 違反していれば
                                else:
                                    # 警告して
                                    show_return_msg(
                                        ReturnMsg.Warn.update_lb_automatically,
                                        parent=self.parent(),
                                        with_cancel_button=False,
                                        additional_message=name,
                                    )
                                    # デフォルト値を計算して設定する
                                    tmp_expression = Expression('0.9 * ' + expression.expr)
                                    item.setData(tmp_expression, Qt.ItemDataRole.UserRole)
                                    display_value = tmp_expression.expr
                                    item.setText(display_value)
                        # 以前にはなかった変数であれば
                        else:
                            # デフォルト値を計算して設定する
                            tmp_expression = Expression('0.9 * ' + expression.expr)
                            item.setData(tmp_expression, Qt.ItemDataRole.UserRole)
                            display_value = tmp_expression.expr
                            item.setText(display_value)

                    c = self.get_column_by_header_data(self.ColumnNames.lower_bound)
                    self.setItem(r, c, item)

                # ===== ub =====
                with nullcontext():
                    item = QStandardItem()
                    # 新しい変数の式が文字式ならとにかく空欄にする
                    if expression.is_expression():
                        display_value = ''
                        item.setText(display_value)

                    # 新しい変数が数値であって、
                    else:
                        # 以前からある変数であって、
                        if name in stashed_data.keys():
                            # 以前は文字式であって空欄が入っていた場合
                            self.set_data_from_stash(item, name, self.ColumnNames.upper_bound, stashed_data)
                            if item.text() == '':
                                # 上の set_data_from_stash を破棄して
                                item = QStandardItem()
                                # デフォルト値を計算して設定する
                                tmp_expression = Expression('1.1 * ' + expression.expr)
                                item.setData(tmp_expression, Qt.ItemDataRole.UserRole)
                                display_value = tmp_expression.expr
                                item.setText(display_value)
                            # 以前から何か数値が入っていた場合
                            else:
                                # 上下限チェックを満たしていれば
                                assert expression.is_number()
                                stashed: Expression = item.data(Qt.ItemDataRole.UserRole)
                                ret_msg, error_nums = check_bounds(expression.value, ub=stashed.value)
                                if ret_msg == ReturnMsg.no_message:
                                    # stash_data をそのまま使う
                                    pass

                                # 違反していれば
                                else:
                                    # 警告して
                                    show_return_msg(
                                        ReturnMsg.Warn.update_ub_automatically,
                                        parent=self.parent(),
                                        with_cancel_button=False,
                                        additional_message=name,
                                    )
                                    # デフォルト値を計算して設定する
                                    tmp_expression = Expression('1.1 * ' + expression.expr)
                                    item.setData(tmp_expression, Qt.ItemDataRole.UserRole)
                                    display_value = tmp_expression.expr
                                    item.setText(display_value)
                        # 以前にはなかった変数であれば
                        else:
                            # デフォルト値を計算して設定する
                            tmp_expression = Expression('1.1 * ' + expression.expr)
                            item.setData(tmp_expression, Qt.ItemDataRole.UserRole)
                            display_value = tmp_expression.expr
                            item.setText(display_value)

                    c = self.get_column_by_header_data(self.ColumnNames.upper_bound)
                    self.setItem(r, c, item)

                # ===== test_value =====
                with nullcontext():
                    item = QStandardItem()
                    # 新しい変数の式が文字式ならとにかくデフォルト値を設定する
                    if expression.is_expression():
                        tmp_expression = Expression(expression.expr)
                        item.setData(tmp_expression, Qt.ItemDataRole.UserRole)
                        item.setText(str(variable_values[name]))

                    # 新しい変数が数値であって、
                    else:

                        # 以前からある変数であって、
                        if name in stashed_data.keys():

                            # 以前は文字式であった場合 (stashed_data の initial_value を調べる)
                            tmp_item = QStandardItem()
                            self.set_data_from_stash(tmp_item, name, self.ColumnNames.initial_value, stashed_data)
                            stashed_expression: Expression = tmp_item.data(Qt.ItemDataRole.UserRole)
                            if stashed_expression.is_expression():
                                # デフォルト値を設定する
                                tmp_expression = Expression(expression.expr)
                                item.setData(tmp_expression, Qt.ItemDataRole.UserRole)
                                item.setText(str(variable_values[name]))

                            # 以前も数値であった場合
                            else:
                                # stash_data を使う
                                self.set_data_from_stash(item, name, self.ColumnNames.test_value, stashed_data)

                        # 以前からない数値であれば
                        else:
                            # デフォルト値を設定する
                            tmp_expression = Expression(expression.expr)
                            item.setData(tmp_expression, Qt.ItemDataRole.UserRole)
                            item.setText(str(variable_values[name]))

                    c = self.get_column_by_header_data(self.ColumnNames.test_value)
                    self.setItem(r, c, item)

                # ===== note =====
                with nullcontext():
                    item = QStandardItem()
                    if name in stashed_data.keys():
                        self.set_data_from_stash(item, name, self.ColumnNames.note, stashed_data)
                    else:
                        item.setText('')
                    c = self.get_column_by_header_data(self.ColumnNames.note)
                    self.setItem(r, c, item)

    def flags(self, index):
        r = index.row()

        # ===== 行全体 =====
        # initial が expression なら disabled
        c_initial_value = self.get_column_by_header_data(value=self.ColumnNames.initial_value)
        expression: Expression = self.item(r, c_initial_value).data(Qt.ItemDataRole.UserRole)
        if expression.is_expression():
            return ~Qt.ItemFlag.ItemIsEnabled

        return super().flags(index)

    def apply_test_values(self):
        # test 列に登録されている変数を取得
        c_var_name = self.get_column_by_header_data(
            self.ColumnNames.name
        )
        c_test_value = self.get_column_by_header_data(
            self.ColumnNames.test_value
        )

        variables = dict()
        if self.with_first_row:
            iterable = range(1, self.rowCount())
        else:
            iterable = range(self.rowCount())
        for r in iterable:
            var_name = self.item(r, c_var_name).text()
            value = self.item(r, c_test_value).text()
            variables.update(
                {var_name: value}
            )

        # Femtet に転送
        return_msg, a_msg = apply_variables(variables)
        show_return_msg(
            return_msg=return_msg,
            parent=self.parent(),
            additional_message=a_msg,
        )


# 個別ページに表示される ItemModel
class VariableItemModelForTableView(StandardItemModelWithoutFirstRow):
    # first row を非表示
    pass


# 一覧 Problem ページに表示される StandardItemModelAsStandardItem 用 ItemModel
class QVariableItemModelForProblem(QSortFilterProxyModelOfStandardItemModel):

    def filterAcceptsColumn(self, source_column: int, source_parent: QModelIndex):

        # test_value を非表示
        source_model: VariableItemModel = self.sourceModel()
        if source_column == get_column_by_header_data(
                source_model,
                VariableColumnNames.test_value
        ):
            return False

        return True


# 個別ページ
class VariableWizardPage(QWizardPage):
    ui: Ui_WizardPage
    source_model: VariableItemModel
    proxy_model: VariableItemModelForTableView
    delegate: VariableTableViewDelegate
    column_resizer: ResizeColumn

    def __init__(self, parent=None, load_femtet_fun: callable = None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_model(load_femtet_fun)
        self.setup_view()
        self.setup_delegate()

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)

    def setup_model(
            self,
            load_femtet_fun=None,
    ):
        self.source_model = get_var_model(self)
        self.proxy_model = VariableItemModelForTableView()
        self.proxy_model.setSourceModel(self.source_model)

        # load_femtet_fun: __main__.py から貰う想定の
        # femtet 全体を load する関数
        self.ui.pushButton_load_prm.clicked.connect(
            (lambda *_: self.source_model.load_femtet())  # debug 用
            if load_femtet_fun is None else
            (lambda *_: load_femtet_fun())
        )

        self.ui.pushButton_test_prm.clicked.connect(
            lambda *_: self.source_model.apply_test_values()
        )

    def setup_view(self):
        view = self.ui.tableView
        view.setModel(self.proxy_model)
        self.column_resizer = ResizeColumn(view)
        self.resize_column()

    def setup_delegate(self):
        self.delegate = VariableTableViewDelegate()
        self.ui.tableView.setItemDelegate(self.delegate)
        self.resize_column()

    def resize_column(self):
        self.column_resizer.resize_all_columns()


if __name__ == '__main__':
    # _WITH_DUMMY = True  # comment out to prevent debug
    # from pyfemtet_opt_gui_2.femtet.mock import get_femtet, get_obj_names  # comment out to prevent debug

    get_femtet()

    app = QApplication()
    app.setStyle('fusion')

    page_obj = VariableWizardPage()
    page_obj.show()

    sys.exit(app.exec())
