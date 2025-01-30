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

from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.common.expression_processor import *
from pyfemtet_opt_gui.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui.common.return_msg import *

import enum
from contextlib import nullcontext

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyfemtet_opt_gui.models.variables.var import VariableItemModel

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

    def __init__(self, var_model: 'VariableItemModel'):
        self.use: bool = None
        self.name: str = None
        self.expression: str = None
        self.lb: float | None = None
        self.ub: float | None = None
        self.var_model: 'VariableItemModel' = var_model

    def finalize_check(self) -> tuple[ReturnMsg, str]:
        # 両方とも指定されていなければエラー
        if self.lb is None and self.ub is None:
            return ReturnMsg.Error.no_bounds, ''

        # 上下関係がおかしければエラー
        if self.lb is not None and self.ub is not None:
            ret_msg, a_msg = check_bounds(None, self.lb, self.ub)
            if ret_msg != ReturnMsg.no_message:
                return ret_msg, a_msg

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
        c = self.get_column_by_header_data(self.ColumnNames.name)
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

    def set_constraint(self, constraint: Constraint, replacing_name: str = None):

        # replacing_name が与えられていれば
        # その item を constraint.name に変名
        if replacing_name is not None:

            # 名前を探す
            for r in self.get_row_iterable():

                # 一致する名前を探す
                c_name = self.get_column_by_header_data(self.ColumnNames.name)
                name = self.item(r, c_name).text()
                if name == replacing_name:
                    # constraint.name に変名
                    self.item(r, c_name).setText(constraint.name)

            # 存在しなければ何かおかしいが、
            # 内部エラーにするほどではない
            else:
                pass

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

        # 名前をキーにして処理すべき行を探索
        for r in self.get_row_iterable():

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
                    item.setData(Expression(constraint.expression),
                                 Qt.ItemDataRole.UserRole)  # Expression に変換したものを UserRole に保管、finalize 出 Expression 二辺っ巻できることは確定している
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

    def get_constraint(self, name: str):
        for r in self.get_row_iterable():

            # 違う名前ならば次へ
            _h = self.ColumnNames.name
            c = self.get_column_by_header_data(_h)
            if name != self.item(r, c).text():
                continue

            # 該当する場合 Constraint オブジェクトを作成
            out = Constraint(var_model=None)
            out.name = name

            # use
            with nullcontext():
                _h = self.ColumnNames.use
                c = self.get_column_by_header_data(_h)
                use = self.item(r, c).checkState() == Qt.CheckState.Checked
                out.use = use

            # expression, expr
            with nullcontext():
                _h = self.ColumnNames.expr
                c = self.get_column_by_header_data(_h)
                item = self.item(r, c)
                expression = item.text()  # expression をそのまま表示

                out.expression = expression

            # lb
            with nullcontext():
                _h = self.ColumnNames.lb
                c = self.get_column_by_header_data(_h)
                item = self.item(r, c)
                data = item.data(Qt.ItemDataRole.UserRole)
                if data is not None:
                    data: Expression
                    assert data.is_number()
                    data = data.value
                out.lb = data

            # ub
            with nullcontext():
                _h = self.ColumnNames.ub
                c = self.get_column_by_header_data(_h)
                item = self.item(r, c)
                data = item.data(Qt.ItemDataRole.UserRole)
                if data is not None:
                    data: Expression
                    assert data.is_number()
                    data = data.value
                out.ub = data

            return out

        else:
            raise RuntimeError(f'constraint named `{name}` is not found.')

    def _output_json(self):
        """

        def constraint_0(_, opt_):
            var = opt_.variables.get_variables()
            a = var['a']
            b = var['b']
            c = var['c']
            return a * (b + c)


        add_constraint(
            name=name,
            fun=constraint_0,
            lower_bound = 1.
            upper_bound = None,
            strict=True,
        )
        """

        constraints: list[Constraint] = [self.get_constraint(name) for name in self.get_constraint_names()]

        out_funcdef = []
        out = []

        fun_name_counter = 0

        for constraint in constraints:

            if not constraint.use:
                continue

            # 式と使う変数名を取得
            expression = constraint.expression.replace('\n', '')
            expr = Expression(expression)
            variable_names = [_s.name for _s in expr._s_expr.free_symbols]

            # def constraint_0 を定義
            fun_name = f'constraint_{fun_name_counter}'
            with nullcontext():
                funcdef = dict(
                    function=fun_name,
                    args=['_', 'opt_'],
                    commands=None,  # 今から足していく
                    ret=expression,
                )

                # def の中身を作成
                commands = []
                with nullcontext():
                    # var = opt_.variables.get_variables()
                    command = dict(
                        ret='var',
                        command='opt_.variables.get_variables',
                        args=dict(),
                    )
                    commands.append(command)

                    # a = var['a']
                    for variable_name in variable_names:
                        command = dict(
                            ret=variable_name,
                            command=f'var["{variable_name}"]'
                        )
                        commands.append(command)

                funcdef.update({'commands': commands})
                out_funcdef.append(funcdef)

            # femopt.add_constraint
            with nullcontext():
                cmd = dict(command='femopt.add_constraint')
                args = dict()

                args.update(
                    dict(
                        name=f'"{constraint.name}"',
                        fun=fun_name,
                        lower_bound=constraint.lb,
                        upper_bound=constraint.ub,
                        strict=True,
                        args=['femopt.opt'],
                    )
                )

                cmd.update({'args': args})
                out.append(cmd)

            fun_name_counter += 1

        return out_funcdef, out

    def output_json(self):
        import json
        return json.dumps(self._output_json()[1])

    def output_funcdef_json(self):
        import json
        return json.dumps(self._output_json()[0])
