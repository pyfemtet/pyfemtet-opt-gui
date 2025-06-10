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
from traceback import print_exception

from pyfemtet_opt_gui.ui.ui_WizardPage_var import Ui_WizardPage

from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui.common.return_msg import *
from pyfemtet_opt_gui.common.expression_processor import *
from pyfemtet_opt_gui.common.titles import *
import pyfemtet_opt_gui.fem_interfaces as fi


# ===== model =====
_VAR_MODEL = None


def get_var_model(parent, _dummy_data=None) -> 'VariableItemModel':
    global _VAR_MODEL
    if _VAR_MODEL is None:
        if not _is_debugging():
            assert parent is not None
        _VAR_MODEL = VariableItemModel(
            parent,
            _dummy_data=(
                _default_dummy_data if _dummy_data is True
                else _dummy_data
            )
        )
    return _VAR_MODEL


def _reset_var_model():
    global _VAR_MODEL
    _VAR_MODEL = None


def get_var_model_for_problem(parent, _dummy_data=None):
    var_model = get_var_model(parent,_dummy_data)
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
    step = 'ステップ'
    test_value = 'テスト値 または\n文字式の計算結果'
    note = 'メモ欄'


# dummy data
_default_dummy_data = {
    VariableColumnNames.use: [True, True, True, False],
    VariableColumnNames.name: ['x1', 'x2', 'x3', 'x4'],
    VariableColumnNames.initial_value: [0., 3.14, 'x1 + x2', 'x1 / x2'],
    VariableColumnNames.lower_bound: [-1, -1, None, None],
    VariableColumnNames.upper_bound: [1, 10., None, None],
    VariableColumnNames.step: [1, None, None, None],
    VariableColumnNames.test_value: [0., 3.14, 'x1 + x2', 'x1 / x2'],
    VariableColumnNames.note: [None, None, None, None],
}


# ===== qt objects =====
# 個別ページに表示される TableView の Delegate
class VariableTableViewDelegate(QStyledItemDelegate):

    @staticmethod
    def get_name(header_data_, model, index):
        # get name of initial_value
        c_ = get_column_by_header_data(model, header_data_)
        index_ = model.index(index.row(), c_)
        name: str = model.data(index_, Qt.ItemDataRole.DisplayRole)
        return name

    @staticmethod
    def get_expression(header_data_, model, index) -> Expression | None:
        # get expression of initial_value
        c_ = get_column_by_header_data(model, header_data_)
        index_ = model.index(index.row(), c_)
        expression_: Expression | None = model.data(index_, Qt.ItemDataRole.UserRole)
        return expression_

    def check_bounds(self, new_expression, header_data, model, index) -> tuple[ReturnType, str | None]:

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

        return check_expr_str_and_bounds(
            init.expr,
            lb.value if lb is not None else None,
            ub.value if ub is not None else None,
            get_var_model(None).get_current_variables(),
        )

    def check_valid(self, text, header_data, model, index) -> tuple[ReturnType, str, Expression | None]:

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
                    return ReturnMsg.no_message, '', new_expression

        # text をチェックする
        try:
            new_expression: Expression = Expression(text)

        # Not a valid expression
        except Exception as e:
            print_exception(e)
            ret_msg = ReturnMsg.Error.cannot_recognize_as_an_expression
            return ret_msg, '', None

        # Valid expression
        if new_expression is not None:

            #  but not a number
            if not new_expression.is_number():

                # if initial_value or test_value, it must be a number.
                if (
                        header_data == VariableColumnNames.initial_value
                        or header_data == VariableColumnNames.step
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
                return ret_msg, '', None

            # but raises other expression's error
            # (for example, division by zero)
            if (
                    header_data == VariableColumnNames.initial_value
                    or header_data == VariableColumnNames.test_value
            ):

                name = self.get_name(VariableColumnNames.name, model, index)
                expressions = get_var_model(self.parent()).get_current_variables()
                expressions.update({name: new_expression})
                _, ret_msg, a_msg = eval_expressions(expressions)
                if ret_msg != ReturnMsg.no_message:
                    return ReturnMsg.Error.raises_other_expression_error, a_msg, None

        # check end
        return ReturnMsg.no_message, '', new_expression

    def setModelData(self, editor, model, index) -> None:

        assert isinstance(model, VariableItemModelForTableView), f'{type(model)=}'

        # QLineEdit を使いたいので str を setText すること

        header_data = get_internal_header_data(index)

        if (
                header_data == VariableColumnNames.initial_value
                or header_data == VariableColumnNames.lower_bound
                or header_data == VariableColumnNames.upper_bound
                or header_data == VariableColumnNames.step
                or header_data == VariableColumnNames.test_value
        ):
            editor: QLineEdit
            text = editor.text()

            # check valid input or not
            if header_data == VariableColumnNames.step:
                # if step, allow empty input
                if text.removeprefix(' ') == '':
                    new_expression = None

                # if step, positive only
                else:
                    ret_msg, a_msg, new_expression = self.check_valid(text, header_data, model, index)
                    if not can_continue(ret_msg, parent=self.parent(), additional_message=text):
                        return

                    assert new_expression is not None
                    if new_expression.value <= 0:
                        ret_msg = ReturnMsg.Error.step_must_be_positive
                        can_continue(ret_msg, parent=self.parent(), additional_message=','.join((text, a_msg)))
                        return

            else:
                ret_msg, a_msg, new_expression = self.check_valid(text, header_data, model, index)
                if not can_continue(ret_msg, parent=self.parent(), additional_message=','.join((text, a_msg))):
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

            # if test, evaluate other expressions
            if (
                    header_data == VariableColumnNames.test_value
            ):
                name = self.get_name(VariableColumnNames.name, model, index)
                ret_msg, a_msg = get_var_model(None).update_test_value_expressions({name: new_expression})
                if not can_continue(ret_msg, parent=self.parent(), additional_message=a_msg):
                    return

            # if OK, update model
            display = new_expression.expr if new_expression is not None else ''
            model.setData(index, display, Qt.ItemDataRole.DisplayRole)
            model.setData(index, new_expression, Qt.ItemDataRole.UserRole)

            return

        return super().setModelData(editor, model, index)


# 大元の ItemModel
# TODO: 変数の一部が更新されても式を再計算していなくない？
class VariableItemModel(StandardItemModelWithHeader):
    ColumnNames = VariableColumnNames

    column_name_display_map = {
        CommonItemColumnName.use: 'パラメータ\nとして使用'
    }

    def _set_dummy_data(self, _dummy_data: dict):

        rows = 1 + len(tuple(_dummy_data.values())[0])
        columns = len(self.ColumnNames)
        self.setRowCount(rows)
        self.setColumnCount(columns)

        variable_values, ret_msg, additional_msg = eval_expressions(
            {
                name: Expression(tst) for name, tst in zip(
                    _dummy_data[self.ColumnNames.name],
                    _dummy_data[self.ColumnNames.test_value]
                )
            }
        )
        assert ret_msg == ReturnMsg.no_message, 'ダミーデータが計算不能'

        iterable = self.get_row_iterable()
        for key, values in _dummy_data.items():
            for i, (r, value) in enumerate(zip(iterable, values)):

                c = self.get_column_by_header_data(key)
                item = QStandardItem()

                # self.ColumnNames.use
                if key == self.ColumnNames.use:
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Checked)
                    item.setEditable(False)

                # self.ColumnNames.name
                elif key == self.ColumnNames.name:
                    item.setText(str(value))
                    item.setEditable(False)

                # self.ColumnNames.initial_value
                # self.ColumnNames.lower_bound
                # self.ColumnNames.upper_bound
                # self.ColumnNames.step
                elif (
                        key == self.ColumnNames.initial_value
                        or key == self.ColumnNames.lower_bound
                        or key == self.ColumnNames.upper_bound
                        or key == self.ColumnNames.step
                ):
                    if value is not None:
                        item.setText(str(value))
                        item.setData(Expression(value), Qt.ItemDataRole.UserRole)

                # self.ColumnNames.test_value
                elif key == self.ColumnNames.test_value:
                    name = _dummy_data[self.ColumnNames.name][i]
                    item.setText(str(variable_values[name]))
                    item.setData(Expression(value), Qt.ItemDataRole.UserRole)

                elif key == self.ColumnNames.note:
                    if value is not None:
                        item.setText(str(value))

                else:
                    raise Exception(f'ダミーデータが不正, {key}')

                self.setItem(r, c, item)

    def load_femtet(self) -> ReturnMsg:
        # variables 取得
        expression: Expression
        expressions: dict[str, Expression]
        expressions, ret_msg = fi.get().get_variables()
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

                # ===== step =====
                with nullcontext():
                    item = QStandardItem()
                    # 新しい変数の式が文字式ならとにかくデフォルト値を設定する
                    if expression.is_expression():
                        item.setData(None, Qt.ItemDataRole.UserRole)
                        item.setText('')

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
                                item.setData(None, Qt.ItemDataRole.UserRole)
                                item.setText('')

                            # 以前も数値であった場合
                            else:
                                # stash_data を使う
                                self.set_data_from_stash(item, name, self.ColumnNames.step, stashed_data)

                        # 以前からない数値であれば
                        else:
                            # デフォルト値を設定する
                            item.setData(None, Qt.ItemDataRole.UserRole)
                            item.setText('')

                    c = self.get_column_by_header_data(self.ColumnNames.step)
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

    def update_test_value_expressions(
            self, partial_expressions: dict[str, Expression] = None
    ) -> tuple[ReturnType, str | None]:
        # QLineEdit を使いたいので str を setText すること

        # 再計算する
        expressions = self.get_current_variables(get_test_Value=True)
        if partial_expressions is not None:
            expressions.update(partial_expressions)
        evaluated_values, ret_msg, a_msg = eval_expressions(expressions)

        # もし計算過程でエラーになっていたらエラーにする
        if ret_msg != ReturnMsg.no_message:
            return ret_msg, a_msg

        # 再計算結果を表示する
        c_var_name = self.get_column_by_header_data(
            self.ColumnNames.name
        )
        c_test_value = self.get_column_by_header_data(
            self.ColumnNames.test_value
        )
        c_initial_value = self.get_column_by_header_data(
            self.ColumnNames.initial_value
        )
        for r in self.get_row_iterable():

            # 変数が expression でなければ無視
            expression: Expression = self.item(r, c_initial_value).data(Qt.ItemDataRole.UserRole)
            if expression is not None:
                if not expression.is_expression():
                    continue

            # 値を更新
            name = self.item(r, c_var_name).text()
            self.item(r, c_test_value).setData(str(evaluated_values[name]), Qt.ItemDataRole.DisplayRole)
            # self.item(r, c_test_value).setData(expressions[name], Qt.ItemDataRole.UserRole)  # なくてもいいはず

        return ReturnMsg.no_message, None

    def apply_test_values(self):

        # test 列に登録されている変数を取得
        c_var_name = self.get_column_by_header_data(
            self.ColumnNames.name
        )
        c_test_value = self.get_column_by_header_data(
            self.ColumnNames.test_value
        )
        c_initial_value = self.get_column_by_header_data(
            self.ColumnNames.initial_value
        )

        variables = dict()
        for r in self.get_row_iterable():

            # 変数が expression なら無視
            expression: Expression = self.item(r, c_initial_value).data(Qt.ItemDataRole.UserRole)
            if expression is not None:
                if expression.is_expression():
                    continue

            # 変数名: 値 の dict を作成
            var_name = self.item(r, c_var_name).text()
            value = self.item(r, c_test_value).text()
            variables.update(
                {var_name: value}
            )

        # Femtet に転送
        return_msg, a_msg = fi.get().apply_variables(variables)
        show_return_msg(
            return_msg=return_msg,
            parent=self.parent(),
            additional_message=a_msg,
        )

    def get_current_variables(self, get_test_Value=False) -> dict[str, Expression]:
        if self.with_first_row:
            iterable = range(1, self.rowCount())
        else:
            iterable = range(0, self.rowCount())
        c_name = self.get_column_by_header_data(self.ColumnNames.name)
        if get_test_Value:
            c_value = self.get_column_by_header_data(self.ColumnNames.test_value)
        else:
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
                        args = list(expr.dependencies)
                        # lambda <args>: eval('<expr>', locals=...)
                        value = (
                                'lambda '
                                + ', '.join(args)
                                + ': '
                                + f'eval("{expr.expr}", dict(**locals(), **get_femtet_builtins()))'
                        )
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

                # step
                with nullcontext():
                    item = self.item(r, self.get_column_by_header_data(self.ColumnNames.step))
                    if item is None:
                        expr: Expression | None = None
                    else:
                        expr: Expression | None = item.data(Qt.ItemDataRole.UserRole)
                    if expr is not None:
                        assert expr.is_number()
                        args_object.update(
                            dict(step=expr.value)
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
                        # 数式ではないのでここには来ないはず
                        assert False
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

    def __init__(
            self,
            parent=None,
            load_femtet_fun: callable = None,
            _dummy_data=None,
    ):
        super().__init__(parent, _dummy_data)
        self.setup_ui()
        self.setup_model(load_femtet_fun)
        self.setup_view()
        self.setup_delegate()

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)
        self.ui.commandLinkButton.clicked.connect(
            lambda *args: fi.get().open_help('ProjectCreation/VariableTree.htm')
        )

    def setup_model(
            self,
            load_femtet_fun=None,
    ):
        self.source_model = get_var_model(self, _dummy_data=self._dummy_data)
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


def _debug():

    from tests import get_test_femprj_path

    fem_gui = fi.get()
    fem_gui.get_femtet()
    assert fem_gui.get_connection_state() == ReturnMsg.no_message
    assert fem_gui._load_femprj(get_test_femprj_path()) is True

    app = QApplication()
    app.setStyle('fusion')

    page_obj = VariableWizardPage(_dummy_data=True)
    page_obj.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    _debug()
