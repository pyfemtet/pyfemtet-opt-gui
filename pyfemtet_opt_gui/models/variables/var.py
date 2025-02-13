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

from pyfemtet_opt_gui.ui.ui_WizardPage_var import Ui_WizardPage

from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui.common.return_msg import *
from pyfemtet_opt_gui.common.expression_processor import *
from pyfemtet_opt_gui.common.titles import *
from pyfemtet_opt_gui.femtet.femtet import *

from pyfemtet_opt_gui.models.constraints.model import Constraint

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
    var_model_for_problem = QVariableItemModelForProblem(parent)
    var_model_for_problem.setSourceModel(var_model)
    return var_model_for_problem


# ===== constants =====
class VariableColumnNames(enum.StrEnum):
    use = CommonItemColumnName.use  # 基幹なので見た目を変更するときは column_name_display_map で
    name = '変数名'
    initial_value = '初期値 または\n文字式'
    lower_bound = '下限'
    upper_bound = '上限'
    test_value = 'テスト値 または\n文字式の計算結果'
    note = 'メモ欄'


# ===== qt objects =====
# 個別ページに表示される TableView の Delegate
class VariableTableViewDelegate(QStyledItemDelegate):

    def get_expression(self, header_data_, model, index) -> Expression | None:
        # get expression of initial_value
        c_ = get_column_by_header_data(model, header_data_)
        index_ = model.index(index.row(), c_)
        expression_: Expression | None = model.data(index_, Qt.ItemDataRole.UserRole)
        return expression_

    def check_bounds(self, new_expression, header_data, model, index) -> tuple[ReturnMsg, str]:

        # get current value
        init: Expression = self.get_expression(VariableColumnNames.initial_value, model, index)
        lb: Expression | None = self.get_expression(VariableColumnNames.lower_bound, model, index)
        ub: Expression | None = self.get_expression(VariableColumnNames.upper_bound, model, index)
        assert isinstance(init, Expression)

        # overwrite it with the new user-input
        with nullcontext():
            if header_data == VariableColumnNames.initial_value:
                init = new_expression
                assert isinstance(init, Expression)

            elif header_data == VariableColumnNames.lower_bound:
                lb = new_expression

            elif header_data == VariableColumnNames.upper_bound:
                ub = new_expression

            else:
                raise NotImplementedError

        # if lb and ub are None, check nothing
        if lb is None and ub is None:
            return ReturnMsg.no_message, None

        # initialize Constraint
        with nullcontext():
            constraint: Constraint = Constraint(get_var_model(None))
            constraint.expression = init.expr
            constraint.lb = lb.value if lb is not None else None
            constraint.ub = ub.value if ub is not None else None

        return constraint.finalize_check()

    def check_valid(self, text, header_data, model, index) -> tuple[ReturnMsg, Expression | None]:

        new_expression: Expression | None = None

        # Femtet に文字式が書いている場合は
        # ub, lb は constraint 扱いなので
        # None でもよい
        expression = self.get_expression(VariableColumnNames.initial_value, model, index)
        assert isinstance(expression, Expression)
        if expression.is_expression():
            if (
                    header_data == VariableColumnNames.lower_bound
                    or header_data == VariableColumnNames.upper_bound
            ):
                if text == '':
                    return ReturnMsg.no_message, new_expression

        # text をチェックする
        try:
            new_expression: Expression = Expression(text)

        # Not a valid expression
        except Exception:
            ret_msg = ReturnMsg.Error.cannot_recognize_as_an_expression
            return ret_msg, None

        # Valid expression
        if new_expression is not None:

            #  but not a number
            if not new_expression.is_number():

                # if initial_value or test_value, it must be a number.
                if (
                        header_data == VariableColumnNames.initial_value
                        or header_data == VariableColumnNames.test_value
                ):
                    ret_msg = ReturnMsg.Error.not_a_number

                # lower_bound or upper_bound must be a number too,
                # but it can be set later, so switch ret_msg.
                elif (
                        header_data == VariableColumnNames.lower_bound
                        or header_data == VariableColumnNames.upper_bound
                ):
                    ret_msg = ReturnMsg.Error.not_a_number_expression_setting_is_enable_in_constraint

                else:
                    raise RuntimeError('Internal Error! Unexpected header_data in VariableTableDelegate.')

                # show error dialog
                return ret_msg, None

        # check end
        return ReturnMsg.no_message, new_expression

    def setModelData(self, editor, model, index) -> None:

        # QLineEdit を使いたいので str を setText すること

        header_data = get_internal_header_data(index)

        if (
                header_data == VariableColumnNames.initial_value
                or header_data == VariableColumnNames.lower_bound
                or header_data == VariableColumnNames.upper_bound
                or header_data == VariableColumnNames.test_value
        ):
            editor: QLineEdit
            text = editor.text()

            # check valid input or not
            ret_msg, new_expression = self.check_valid(text, header_data, model, index)
            if not can_continue(ret_msg, parent=self.parent(), additional_message=text):
                return

            # if init or lb or ub, check bounds
            if (
                    header_data == VariableColumnNames.initial_value
                    or header_data == VariableColumnNames.lower_bound
                    or header_data == VariableColumnNames.upper_bound
            ):
                ret_msg, a_msg = self.check_bounds(new_expression, header_data, model, index)
                if not can_continue(ret_msg, parent=self.parent(), additional_message=a_msg):
                    return

            # if OK, update model
            display = new_expression.expr if new_expression is not None else ''
            model.setData(index, display, Qt.ItemDataRole.DisplayRole)
            model.setData(index, new_expression, Qt.ItemDataRole.UserRole)
            return

        return super().setModelData(editor, model, index)


# 大元の ItemModel
class VariableItemModel(StandardItemModelWithHeader):
    ColumnNames = VariableColumnNames

    column_name_display_map = {
        CommonItemColumnName.use: 'パラメータ\nとして使用'
    }

    def _set_dummy_data(self, n_rows=None):
        rows = n_rows if n_rows is not None else 3
        columns = len(self.ColumnNames)

        if self.with_first_row:
            rows += 1
            iterable = range(1, rows)
        else:
            iterable = range(0, rows)

        with EditModel(self):
            self.setRowCount(rows)
            self.setColumnCount(columns)

        with EditModel(self):
            for r in iterable:
                # self.ColumnNames.use
                with nullcontext():
                    _h = self.ColumnNames.use
                    c = self.get_column_by_header_data(_h)

                    item = QStandardItem()
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Checked)
                    item.setEditable(False)

                    self.setItem(r, c, item)

                # self.ColumnNames.name
                with nullcontext():
                    _h = self.ColumnNames.name
                    c = self.get_column_by_header_data(_h)

                    item = QStandardItem()
                    item.setText(f'name{r}')
                    item.setEditable(False)

                    self.setItem(r, c, item)

                # self.ColumnNames.initial_value
                with nullcontext():
                    _h = self.ColumnNames.initial_value
                    c = self.get_column_by_header_data(_h)

                    item = QStandardItem()
                    item.setText(f'{r}')
                    item.setData(Expression(f'{r}'), Qt.ItemDataRole.UserRole)

                    self.setItem(r, c, item)

                # self.ColumnNames.lower_bound
                with nullcontext():
                    _h = self.ColumnNames.lower_bound
                    c = self.get_column_by_header_data(_h)

                    item = QStandardItem()
                    item.setText(f'{r - 1}')
                    item.setData(Expression(f'{r - 1}'), Qt.ItemDataRole.UserRole)

                    self.setItem(r, c, item)

                # self.ColumnNames.upper_bound
                with nullcontext():
                    _h = self.ColumnNames.upper_bound
                    c = self.get_column_by_header_data(_h)

                    item = QStandardItem()
                    item.setText(f'{r + 1}')
                    item.setData(Expression(f'{r + 1}'), Qt.ItemDataRole.UserRole)

                    self.setItem(r, c, item)

                # self.ColumnNames.test_value
                with nullcontext():
                    _h = self.ColumnNames.test_value
                    c = self.get_column_by_header_data(_h)

                    item = QStandardItem()
                    item.setText(f'{r + 1}')
                    item.setData(Expression(f'{r + 1}'), Qt.ItemDataRole.UserRole)

                    self.setItem(r, c, item)

                # self.ColumnNames.note
                with nullcontext():
                    _h = self.ColumnNames.note
                    c = self.get_column_by_header_data(_h)

                    item = QStandardItem()
                    item.setText(f'{r + 1}')

                    self.setItem(r, c, item)

    def load_femtet(self) -> ReturnMsg:
        # variables 取得
        expression: Expression
        expressions: dict[str, Expression]
        expressions, ret_msg = get_variables()
        if not can_continue(ret_msg, self.parent()):
            return ret_msg

        # variables の評価
        # Femtet から取得してもよいが、
        # initial_value が stash されたものを
        # 使う仕様に変える可能性があるため
        variable_values, ret_msg, additional_msg = eval_expressions(expressions)
        if not can_continue(ret_msg, self.parent(), additional_message=additional_msg):
            return ret_msg

        # 現在の状態を stash
        stashed_data = self.stash_current_table()

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
                        item.setToolTip('式が文字式であるため選択できません。')
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
                    if expression.is_expression():
                        item.setToolTip('式が文字式であるため編集できません。')
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

        return ReturnMsg.no_message

    def flags(self, index):
        r = index.row()
        c = index.column()

        # ===== 行全体を Un-selectable =====

        # ただし lb、ub、note は除く
        if (
                c == self.get_column_by_header_data(self.ColumnNames.lower_bound)
                or c == self.get_column_by_header_data(self.ColumnNames.upper_bound)
                or c == self.get_column_by_header_data(self.ColumnNames.note)
        ):
            return super().flags(index)

        # initial が expression なら enabled (not editable)
        c_initial_value = self.get_column_by_header_data(value=self.ColumnNames.initial_value)
        expression: Expression = self.item(r, c_initial_value).data(Qt.ItemDataRole.UserRole)
        if expression is not None:
            if expression.is_expression():
                return Qt.ItemFlag.ItemIsEnabled

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

    def get_current_variables(self) -> dict[str, Expression]:
        if self.with_first_row:
            iterable = range(1, self.rowCount())
        else:
            iterable = range(0, self.rowCount())
        c_name = self.get_column_by_header_data(self.ColumnNames.name)
        c_value = self.get_column_by_header_data(self.ColumnNames.initial_value)
        out = dict()
        for r in iterable:
            name = self.item(r, c_name).text()
            index = self.index(r, c_value)
            expr: Expression = self.data(index, Qt.ItemDataRole.UserRole)
            out.update({name: expr})
        return out

    def is_nothing_checked(self) -> bool:
        # ひとつも used がなければ False
        hd = self.ColumnNames.use
        c = self.get_column_by_header_data(hd)
        check_list = []
        for r in self.get_row_iterable():
            check_list.append(self.item(r, c).checkState())
        # Checked がひとつもない
        return all([ch != Qt.CheckState.Checked for ch in check_list])

    def output_json(self) -> str:
        """Use 列が Checked のものを json 形式にして出力"""

        out_object = list()

        for r in self.get_row_iterable():

            # 必要な列の logicalIndex を取得
            hd = self.ColumnNames.use
            c = self.get_column_by_header_data(hd)

            # 出力オブジェクトの準備
            command_object = dict()
            args_object = dict()

            # 最適化に関与しない数式。pass_to_fem を False にしないと
            # Femtet の数式を数値で上書きしてしまうが、
            # これを追加しないとこの数式を参照した拘束式などが
            # 評価できない
            # add_expression(pass_to_fem=False)
            if not self.item(r, c).isCheckable():

                command_object.update(
                    {'command': 'femopt.add_expression'}
                )

                # name
                with nullcontext():
                    item = self.item(r, self.get_column_by_header_data(self.ColumnNames.name))
                    args_object.update(
                        dict(name=f'"{item.text()}"')
                    )

                # fun
                with nullcontext():
                    item = self.item(r, self.get_column_by_header_data(self.ColumnNames.initial_value))
                    expr: Expression = item.data(Qt.ItemDataRole.UserRole)
                    if expr.is_number():
                        value = f'lambda: {expr.value}'
                    else:
                        args = [symbol.name for symbol in expr._s_expr.free_symbols]
                        # lambda <args>: <expr>
                        value = 'lambda ' + ', '.join(args) + ': ' + expr.expr
                    args_object.update(
                        dict(fun=value)
                    )

                # pass_to_fem
                with nullcontext():
                    args_object.update(
                        dict(pass_to_fem=False)
                    )

            # 数式でなくて Check されている場合: 通常の Parameter
            # add_parameter
            elif self.item(r, c).checkState() == Qt.CheckState.Checked:

                command_object.update(
                    {'command': 'femopt.add_parameter'}
                )

                args_object = dict()

                # name
                with nullcontext():
                    item = self.item(r, self.get_column_by_header_data(self.ColumnNames.name))
                    args_object.update(
                        dict(name=f'"{item.text()}"')
                    )

                # initial_value
                with nullcontext():
                    item = self.item(r, self.get_column_by_header_data(self.ColumnNames.initial_value))
                    expr: Expression = item.data(Qt.ItemDataRole.UserRole)
                    assert expr.is_number()
                    args_object.update(
                        dict(initial_value=expr.value)
                    )

                # lower_bound
                with nullcontext():
                    item = self.item(r, self.get_column_by_header_data(self.ColumnNames.lower_bound))
                    expr: Expression = item.data(Qt.ItemDataRole.UserRole)
                    assert expr.is_number()
                    args_object.update(
                        dict(lower_bound=expr.value)
                    )

                # upper_bound
                with nullcontext():
                    item = self.item(r, self.get_column_by_header_data(self.ColumnNames.upper_bound))
                    expr: Expression = item.data(Qt.ItemDataRole.UserRole)
                    assert expr.is_number()
                    args_object.update(
                        dict(upper_bound=expr.value)
                    )

            # 数式でなくて Check されていない場合: Expression (pass_to_fem=True)
            # GUI 画面と Femtet の定義に万一差があっても
            # pass_to_fem が True なら上書きできる。
            # add_expression
            else:

                command_object.update(
                    {'command': 'femopt.add_expression'}
                )

                # name
                with nullcontext():
                    item = self.item(r, self.get_column_by_header_data(self.ColumnNames.name))
                    args_object.update(
                        dict(name=f'"{item.text()}"')
                    )

                # fun
                with nullcontext():
                    item = self.item(r, self.get_column_by_header_data(self.ColumnNames.initial_value))
                    expr: Expression = item.data(Qt.ItemDataRole.UserRole)
                    if expr.is_number():
                        value = f'lambda: {expr.value}'
                    else:
                        args = [symbol.name for symbol in expr._s_expr.free_symbols]
                        # lambda <args>: <expr>
                        value = 'lambda ' + ', '.join(args) + ': ' + expr.expr
                    args_object.update(
                        dict(fun=value)
                    )

                # pass_to_fem
                with nullcontext():
                    args_object.update(
                        dict(pass_to_fem=True)
                    )

            command_object.update({'args': args_object})
            out_object.append(command_object)

        import json
        return json.dumps(out_object)

    def output_expression_constraint_json(self) -> str:
        """
        femopt.add_constraint(
            name='var_name',
            fun=lambda opt_: opt['var_name'],  # output_json で add_expression しているのでこれで動作する
            lower_bound=...,
            upper_bound=...,
            strict=True,
            args=(opt,)
        )
        """

        out_object = list()

        for r in self.get_row_iterable():

            # 必要な列の logicalIndex を取得
            with nullcontext():

                hd = self.ColumnNames.name
                c_name = self.get_column_by_header_data(hd)

                hd = self.ColumnNames.initial_value
                c_initial_value = self.get_column_by_header_data(hd)

                hd = self.ColumnNames.lower_bound
                c_lb = self.get_column_by_header_data(hd)

                hd = self.ColumnNames.upper_bound
                c_ub = self.get_column_by_header_data(hd)

            # 出力オブジェクトの準備
            command_object = dict()
            args_object = dict()

            # item を取得
            item_name = self.item(r, c_name)
            item_expression = self.item(r, c_initial_value)
            item_lb = self.item(r, c_lb)
            item_ub = self.item(r, c_ub)

            # item が expression でなければ無視
            if not Expression(item_expression.text()).is_expression():
                continue

            # lb, ub
            expression = item_lb.data(Qt.ItemDataRole.UserRole)
            lb = expression.value if expression is not None else None
            expression = item_ub.data(Qt.ItemDataRole.UserRole)
            ub = expression.value if expression is not None else None

            # ub, lb が None なら無視
            if ub is None and lb is None:
                continue

            # command object の組立
            args_object.update(
                dict(
                    name=f'"constraint_{item_name.text()}"',
                    fun=f'lambda opt_: opt_["{item_name.text()}"]',
                    lower_bound=lb,
                    upper_bound=ub,
                    strict=True,
                    args=['femopt.opt']
                )
            )

            command_object.update(
                {
                    'command': 'femopt.add_constraint',
                    'args': args_object
                }
            )

            out_object.append(command_object)

        import json
        return json.dumps(out_object)


# 個別ページに表示される ItemModel
class VariableItemModelForTableView(StandardItemModelWithoutFirstRow):
    # first row を非表示
    pass


# 一覧 Problem ページに表示される StandardItemModelAsStandardItem 用 ItemModel
class QVariableItemModelForProblem(ProxyModelWithForProblem):

    def filterAcceptsColumn(self, source_column: int, source_parent: QModelIndex):
        # test_value を非表示
        source_model: VariableItemModel = self.sourceModel()
        if source_column == get_column_by_header_data(
                source_model,
                VariableColumnNames.test_value
        ):
            return False

        return super().filterAcceptsColumn(source_column, source_parent)


# 個別ページ
class VariableWizardPage(TitledWizardPage):
    ui: Ui_WizardPage
    source_model: VariableItemModel
    proxy_model: VariableItemModelForTableView
    delegate: VariableTableViewDelegate
    column_resizer: ResizeColumn

    page_name = PageSubTitles.var

    def __init__(self, parent=None, load_femtet_fun: callable = None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_model(load_femtet_fun)
        self.setup_view()
        self.setup_delegate()

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)
        self.ui.commandLinkButton.clicked.connect(
            lambda *args: open_help('ProjectCreation/VariableTree.htm')
        )

    def setup_model(
            self,
            load_femtet_fun=None,
    ):
        self.source_model = get_var_model(self)
        self.proxy_model = VariableItemModelForTableView(self)
        self.proxy_model.setSourceModel(self.source_model)

        # load_femtet_fun: __main__.py から貰う想定の
        # femtet 全体を load する関数
        self.ui.pushButton_load_prm.clicked.connect(
            (lambda *_: self.source_model.load_femtet())  # debug 用
            if load_femtet_fun is None else
            (lambda *_: load_femtet_fun())
        )

        # test value を Femtet に転送する
        self.ui.pushButton_test_prm.clicked.connect(
            lambda *_: self.source_model.apply_test_values()
        )

        # model の checkState が変更されたら
        # isComplete を更新する
        def filter_role(_1, _2, roles):
            if Qt.ItemDataRole.CheckStateRole in roles:  # or len(roles) == 0

                # 警告を表示する（編集は受け入れる）
                if self.source_model.is_nothing_checked():
                    ret_msg = ReturnMsg.Warn.no_params_selected
                    show_return_msg(return_msg=ret_msg, parent=self)

                self.completeChanged.emit()

        self.source_model.dataChanged.connect(filter_role)

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

    def isComplete(self) -> bool:
        if self.source_model.is_nothing_checked():
            return False
        else:
            return True


if __name__ == '__main__':
    # _WITH_DUMMY = True  # comment out to prevent debug
    # from pyfemtet_opt_gui.femtet.mock import get_femtet, get_obj_names  # comment out to prevent debug

    get_femtet()

    app = QApplication()
    app.setStyle('fusion')

    page_obj = VariableWizardPage()
    page_obj.show()

    sys.exit(app.exec())
