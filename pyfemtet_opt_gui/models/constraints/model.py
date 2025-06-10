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
from pyfemtet_opt_gui.models.variables.var import VariableItemModel, get_var_model

import enum
from contextlib import nullcontext
from packaging.version import Version

import pyfemtet


# ===== model singleton pattern =====
_CNS_MODEL = None
_WITH_DUMMY = False


def get_cns_model(parent=None, _dummy_data=None):
    global _CNS_MODEL
    if _CNS_MODEL is None:
        _CNS_MODEL = ConstraintModel(
            parent=parent,
            _dummy_data=(
                _default_dummy_data if _dummy_data is True
                else _dummy_data
            ),
        )
    return _CNS_MODEL


def _reset_cns_model():
    global _CNS_MODEL
    _CNS_MODEL = None


# ===== header data =====
class ConstraintColumnNames(enum.StrEnum):
    use = CommonItemColumnName.use
    name = '名前'
    expr = '式'
    lb = '下限'
    ub = '上限'
    note = 'メモ欄'


_default_dummy_data = {
    ConstraintColumnNames.use: [True, True, True],
    ConstraintColumnNames.name: ['cns1', 'cns2', 'cns3'],
    ConstraintColumnNames.expr: ['x1', 'x1 + x2', 'x1 - x3'],
    ConstraintColumnNames.lb: [0, None, -3.14],
    ConstraintColumnNames.ub: [None, 1, 3.14],
    ConstraintColumnNames.note: [None, None, None],
}


# ===== intermediate data =====

class Constraint:

    def __init__(self, var_model: 'VariableItemModel'):
        self.use: bool = None
        self.name: str = None
        self.expression: str = None
        self.lb: float | None = None
        self.ub: float | None = None
        self.var_model: 'VariableItemModel' = var_model

    def finalize_check(self) -> tuple[ReturnType, str]:

        return check_expr_str_and_bounds(
            self.expression,
            self.lb,
            self.ub,
            self.var_model.get_current_variables(),
        )


# ===== Qt objects =====
# 大元のモデル
class ConstraintModel(StandardItemModelWithHeader):
    ColumnNames = ConstraintColumnNames

    def _set_dummy_data(self, _dummy_data: dict):

        var = _dummy_data.get('var_model', None)
        if var is None:
            # ここで import すると singleton が壊れる
            var = get_var_model(self.parent(), _dummy_data=True)

        rows = 1
        columns = len(self.ColumnNames)
        self.setRowCount(rows)
        self.setColumnCount(columns)

        for i in range(len(tuple(_dummy_data.values())[0])):
            dummy_constraint_data = {}
            for key, values in _dummy_data.items():
                value = tuple(values)[i]
                dummy_constraint_data.update({key: value})

            dummy_cns: Constraint = Constraint(var)
            dummy_cns.use = dummy_constraint_data[self.ColumnNames.use]
            dummy_cns.name = dummy_constraint_data[self.ColumnNames.name]
            dummy_cns.expression = dummy_constraint_data[self.ColumnNames.expr]
            dummy_cns.lb = dummy_constraint_data[self.ColumnNames.lb]
            dummy_cns.ub = dummy_constraint_data[self.ColumnNames.ub]
            self.set_constraint(dummy_cns)

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

        out = [self.item(r, c).text() if self.item(r, c) is not None else None for r in iterable]

        return out

    def delete_constraint(self, name_to_delete):

        # 名前を探す
        for r in self.get_row_iterable():

            # 一致する名前を探して index.Row を取得
            c = self.get_column_by_header_data(self.ColumnNames.name)
            name = self.item(r, c).text()
            if name == name_to_delete:
                target_index = self.index(r, c)
                break

        # 存在しなければ何かおかしい
        else:
            show_return_msg(
                ReturnMsg.Error.no_such_constraint,
                parent=self.parent(),
                additional_message=name_to_delete,
            )
            return

        # 行を削除
        self.removeRow(target_index.row())

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

    def _output_json(self, for_surrogate_model=False):
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
            strict=True
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
            expr_str = constraint.expression.replace('\n', '')
            expr = Expression(expr_str)

            # def constraint_0 を定義
            fun_name = f'constraint_{fun_name_counter}'
            with nullcontext():

                funcdef = dict(
                    function=fun_name,
                    args=['_', 'opt_'],

                    # locals に渡すための辞書 var を後で足す
                    commands=None,

                    # locals を使いたいので eval を返す
                    ret=f'eval("{expr._converted_expr_str}", '
                        f'dict(**locals(), **get_femtet_builtins(var)))',
                )

                # def の中身を作成
                commands = []
                with nullcontext():

                    if Version(pyfemtet.__version__) < Version('0.999.999'):
                        # var = opt_.variables.get_variables()
                        command = dict(
                            ret='var',
                            command='opt_.variables.get_variables',
                            args=dict(),
                        )
                        commands.append(command)

                    else:
                        # var = opt_.get_variables()
                        command = dict(
                            ret='var',
                            command='opt_.get_variables',
                            args=dict(),
                        )
                        commands.append(command)

                funcdef.update({'commands': commands})
                out_funcdef.append(funcdef)

            # femopt.add_constraint
            with nullcontext():
                cmd = dict(command='femopt.add_constraint')
                args = dict()

                if for_surrogate_model:
                    if Version(pyfemtet.__version__) < Version('0.999.999'):
                        cmd_args = ['None', 'femopt.opt']
                    else:
                        cmd_args = ['femopt.opt']
                else:
                    cmd_args = ['femopt.opt']

                args.update(
                    dict(
                        name=f'"{constraint.name}"',
                        fun=fun_name,
                        lower_bound=constraint.lb,
                        upper_bound=constraint.ub,
                        strict=True,
                        args=cmd_args,
                    )
                )

                cmd.update({'args': args})
                out.append(cmd)

            fun_name_counter += 1

        return out_funcdef, out

    def output_json(self, for_surrogate_model=False):
        import json
        return json.dumps(self._output_json(for_surrogate_model)[1])

    def output_funcdef_json(self):
        import json
        return json.dumps(self._output_json()[0])
