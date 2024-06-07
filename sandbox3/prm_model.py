from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem

import _p

from item_as_model import MyStandardItemAsTableModel, _isnumeric


class PrmModel(MyStandardItemAsTableModel):
    """A table for determining whether to use Femtet variables in optimization.

    use        | name       | expression   | lb             | ub             | test
    -------------------------------------------------------------------------
    checkbox   | str        | float or str | float or empty | float or empty | float
    uneditable | uneditable |              |

    note: if expression is not numeric, disable the row (including use column).
    note: expression, lb, ub, test must be a float.
    note: if checkbox is false, disable the row (excluding use column).
    note: must be (lb < expression < ub).

    """

    def load(self):
        # initialize table
        table: QStandardItem = self._item
        table.clearData()
        table.setText('prm')
        table.setRowCount(0)
        table.setColumnCount(6)

        self._root.setColumnCount(max(self._root.columnCount(), table.columnCount()))
        # table.parent().setColumnCount(max(table.parent().columnCount(), table.columnCount()))

        # if Femtet is not alive, do nothing
        if not _p.check_femtet_alive():
            _p.logger.warning('Femtet との接続ができていません。')
            return False

        # load prm
        names = _p.Femtet.GetVariableNames_py()

        # TODO: if no prm, show warning dialog
        if names is None:
            _p.logger.warning('Femtet で変数を設定してください。')
            return False
        elif len(names) == 0:
            _p.logger.warning('Femtet で変数を設定してください。')
            return False

        # notify to start editing to the abstract model
        self.beginResetModel()

        # set data to table
        table.setRowCount(len(names))

        self.set_header([
            'use',
            'name',
            'expression',
            'lb',
            'ub',
            'test',
        ])

        for row, name in enumerate(names):
            # use
            item = QStandardItem()
            item.setCheckable(True)
            table.setChild(row, 0, item)

            # name
            item = QStandardItem(name)
            table.setChild(row, 1, item)

            # expression
            exp = str(_p.Femtet.GetVariableExpression(name))
            item = QStandardItem(exp)
            table.setChild(row, 2, item)

            # lb
            lb = str(float(exp)-1.0) if _isnumeric(exp) else None
            item = QStandardItem(lb)
            table.setChild(row, 3, item)

            # ub
            ub = str(float(exp)+1.0) if _isnumeric(exp) else None
            item = QStandardItem(ub)
            table.setChild(row, 4, item)

            # test
            test = exp if _isnumeric(exp) else None
            item = QStandardItem(test)
            table.setChild(row, 5, item)

        # notify to end editing to the abstract model
        self.endResetModel()

    def flags(self, index):
        if not index.isValid(): return super().flags(index)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        # note: if expression is not numeric, disable the row (including use column).
        exp_col = self.get_col_from_name('expression')
        exp_index = self.createIndex(row, exp_col)
        if not _isnumeric(self.data(exp_index)):
            return ~Qt.ItemIsEnabled

        # note: expression, lb, ub, test must be a float.
        # implemented in setData

        # note: if checkbox is false, disable the row (excluding use column).
        use_col = self.get_col_from_name('use')
        use_item = self.get_item(row, use_col)
        if use_item.checkState() == Qt.CheckState.Unchecked:
            if col_name != 'use':
                return ~Qt.ItemIsEnabled

        # note: must be (lb < expression < ub).
        # implemented in setData

        return super().flags(index)

    def setData(self, index, value, role=Qt.EditRole) -> bool:
        if not index.isValid(): return super().setData(index, value, role)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        # note: expression, lb, ub, test must be a float.
        if col_name in ['expression', 'lb', 'ub']:
            if not _isnumeric(value):
                _p.logger.warning('数値を入力してください。')
                return False

        # note: must be (lb < expression < ub).
        if col_name in ['expression', 'lb', 'ub']:
            exp_index = self.createIndex(row, self.get_col_from_name('expression'))
            exp_float = float(value) if col_name == 'expression' else float(self.data(exp_index))

            lb_index = self.createIndex(row, self.get_col_from_name('lb'))
            lb_float = float(value) if col_name == 'lb' else float(self.data(lb_index))

            ub_index = self.createIndex(row, self.get_col_from_name('ub'))
            ub_float = float(value) if col_name == 'ub' else float(self.data(ub_index))

            if not (lb_float <= exp_float):
                _p.logger.warning('初期値が下限を下回っています。')
                return False

            if not (exp_float <= ub_float):
                _p.logger.warning('初期値が上限を上回っています。')
                return False

            if lb_float == ub_float:
                _p.logger.warning('上限と下限が一致しています。変数の値を変更したくない場合は、use 列のチェックを外してください。')
                return False

        return super().setData(index, value, role)
