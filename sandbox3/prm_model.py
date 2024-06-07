from PySide6.QtGui import QStandardItem

import _p

from item_as_model import MyStandardItemAsTableModel, _isnumeric


class PrmModel(MyStandardItemAsTableModel):

    def load(self):
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
