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

from pyfemtet_opt_gui_2.ui.ui_WizardPage_cns import Ui_WizardPage

from pyfemtet_opt_gui_2.common.qt_util import *
from pyfemtet_opt_gui_2.common.expression_processor import *
from pyfemtet_opt_gui_2.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui_2.common.return_msg import *
from pyfemtet_opt_gui_2.femtet.femtet import *

import enum
import sys
from contextlib import nullcontext

# ===== model singleton pattern =====
_CNS_MODEL = None
_WITH_DUMMY = False


def get_cns_model(parent=None, _with_dummy=None):
    global _CNS_MODEL
    if _CNS_MODEL is None:
        _CNS_MODEL = ConstraintModel(
            parent=parent,
            _with_dummy=_with_dummy if _with_dummy is not None else _WITH_DUMMY,
        )
    return _CNS_MODEL


# ===== header data =====
class ConstraintColumnNames(enum.StrEnum):
    use = CommonItemColumnName.use
    name = '名前'
    expr = '式'
    lb = '下限'
    ub = '上限'
    note = 'メモ欄'


# ===== intermediate data =====

class Constraint:
    name: str | None
    expression: str | None
    lb: float | None
    ub: float | None

    def __init__(self, var_model):
        self.name = None
        self.expression = None
        self.lb = None
        self.ub = None
        self.var_model = var_model

    def finalize_check(self) -> tuple[ReturnMsg, str]:
        # 上下限の関係がおかしければエラー
        if self.lb is None and self.ub is None:
            return ReturnMsg.Error.no_bounds, ''

        if self.lb is not None and self.ub is not None:
            return ReturnMsg.Error.inconsistent_lb_ub, ''

        # expression が None ならエラー
        if self.expression is None:
            return ReturnMsg.Error.cannot_recognize_as_an_expression, '式が入力されていません。'

        # expression が None でなくとも
        # Expression にできなければエラー
        try:
            _expr = Expression(self.expression)
        except SympifyError:
            return ReturnMsg.Error.cannot_recognize_as_an_expression, self.expression

        # Expression にできても値が
        # 計算できなければエラー
        _expr_key = 'this_is_a_target_constraint_expression'
        expressions = self.var_model.get_current_variables()
        expressions.update(
            {_expr_key: _expr}
        )
        ret, ret_msg, a_msg = eval_expressions(expressions)
        a_msg = a_msg.replace(_expr_key, self.expression)
        if ret_msg != ReturnMsg.no_message:
            return ret_msg, a_msg

        # Expression の計算ができても
        # lb, ub との上下関係がおかしければ
        # Warning
        if _expr_key not in ret.keys():
            raise RuntimeError('Internal Error!')
        if not isinstance(ret[_expr_key], float):
            raise RuntimeError('Internal Error!')
        evaluated = ret[_expr_key]
        ret_msg, a_msg = check_bounds(evaluated, self.lb, self.ub)
        if ret_msg != ReturnMsg.no_message:
            return ReturnMsg.Warn.inconsistent_value_bounds, ''

        # 何もなければ no_msg
        return ReturnMsg.no_message, ''


# ===== Qt objects =====
# 大元のモデル
class ConstraintModel(StandardItemModelWithHeader):
    ColumnNames = ConstraintColumnNames

    def get_unique_name(self):
        # get constraint names
        c = self.ColumnNames.name
        if self.with_first_row:
            iterable = range(1, self.rowCount())
        else:
            iterable = range(self.rowCount())
        names = []
        for r in iterable:
            names.append(self.item(r, c).text())

        # unique name
        counter = 0
        candidate = f'cns_{counter}'
        while candidate in names:
            counter += 1
            candidate = f'cns_{counter}'
        return candidate

    def get_constraint_names(self):
        if self.with_first_row:
            iterable = range(1, self.rowCount())
        else:
            iterable = range(0, self.rowCount())

        _h = self.ColumnNames.name
        c = self.get_column_by_header_data(_h)

        out = [self.item(r, c).text() for r in iterable]

        return out

    def set_constraint(self, constraint: Constraint):

        # 名前が存在しないなら行追加
        if constraint.name not in self.get_constraint_names():
            with EditModel(self):
                self.setRowCount(self.rowCount() + 1)

            with EditModel(self):
                r = self.rowCount() - 1
                # name, 一時的なアイテム
                _h = self.ColumnNames.name
                c = self.get_column_by_header_data(_h)
                self.setItem(r, c, QStandardItem(constraint.name))

        if self.with_first_row:
            iterable = range(1, self.rowCount())
        else:
            iterable = range(0, self.rowCount())

        for r in iterable:

            # 一致する名前を探して constraint を parse
            _h = self.ColumnNames.name
            c = self.get_column_by_header_data(_h)
            name = self.item(r, c).text()

            # 違う名前なら無視
            if name != constraint.name:
                continue

            # 一致する名前なので処理
            with EditModel(self):
                # 行追加の際に name のみ一時的な Item を
                # 追加していたが、他の列と一緒に
                # ここで一貫した書き方で設定する

                # use
                with nullcontext():
                    _h = self.ColumnNames.use
                    c = self.get_column_by_header_data(_h)
                    item = QStandardItem()
                    item.setEditable(False)  # 編集不可
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Checked)
                    self.setItem(r, c, item)

                # name
                with nullcontext():
                    # 該当する名前ならば name の useRole に
                    # Constraint オブジェクトを登録
                    _h = self.ColumnNames.name
                    c = self.get_column_by_header_data(_h)
                    item = QStandardItem()
                    item.setText(constraint.name)  # 名前
                    item.setEditable(False)  # 編集不可
                    item.setData(constraint, Qt.ItemDataRole.UserRole)  # UserRole に Constraint を保管
                    self.setItem(r, c, item)

                # expression, expr
                with nullcontext():
                    _h = self.ColumnNames.expr
                    c = self.get_column_by_header_data(_h)
                    item = QStandardItem()
                    item.setEditable(False)  # 編集不可
                    item.setText(constraint.expression)  # expression をそのまま表示
                    item.setData(Expression(constraint.expression), Qt.ItemDataRole.UserRole)  # Expression に変換したものを UserRole に保管、finalize 出 Expression 二辺っ巻できることは確定している
                    self.setItem(r, c, item)

                # lb
                with nullcontext():
                    _h = self.ColumnNames.lb
                    c = self.get_column_by_header_data(_h)
                    item = QStandardItem()
                    item.setEditable(False)  # 編集不可
                    if constraint.lb is not None:
                        expr = Expression(constraint.lb)
                        item.setText(expr.expr)
                        item.setData(expr, Qt.ItemDataRole.UserRole)
                    else:
                        item.setText('なし')
                        item.setData(None, Qt.ItemDataRole.UserRole)
                    self.setItem(r, c, item)

                # ub
                with nullcontext():
                    _h = self.ColumnNames.ub
                    c = self.get_column_by_header_data(_h)
                    item = QStandardItem()
                    item.setEditable(False)  # 編集不可
                    if constraint.ub is not None:
                        expr = Expression(constraint.ub)
                        item.setText(expr.expr)
                        item.setData(expr, Qt.ItemDataRole.UserRole)
                    else:
                        item.setText('なし')
                        item.setData(None, Qt.ItemDataRole.UserRole)
                    self.setItem(r, c, item)

                # note
                with nullcontext():
                    _h = self.ColumnNames.note
                    c = self.get_column_by_header_data(_h)
                    item = QStandardItem()
                    self.setItem(r, c, item)

            # 処理したので終了
            break

