from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import Qt, QAbstractTableModel

import _p


def _isnumeric(exp):
    try:
        float(str(exp))
        isnumeric = True
    except ValueError:
        isnumeric = False
    return isnumeric


class MyStandardItemAsTableModel(QAbstractTableModel):
    def __init__(self, table_item: QStandardItem, parent=None):
        self._item: QStandardItem = table_item  # QStandardItem what has table structure children.
        self._header: list[str] = []
        super().__init__(parent)

    def rowCount(self, parent=None): return self._item.rowCount()
    def columnCount(self, parent=None): return self._item.columnCount()

    def flags(self, index):
        if not index.isValid(): return
        row, col = index.row(), index.column()
        return self._item.child(row, col).flags()

    def data(self, index, role=Qt.EditRole):
        if not index.isValid(): return
        row, col = index.row(), index.column()
        return self._item.child(row, col).data(role)

    def setData(self, index, value, role=Qt.EditRole) -> bool:
        if not index.isValid(): return False
        row, col = index.row(), index.column()
        self._item.child(row, col).setData(value, role)  # -> None
        self.dataChanged.emit(self.createIndex(row, col), self.createIndex(row, col))
        return True

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.get_header(section)
        return None

    def set_header(self, header: list[str]) -> None:
        self._header = header

    def get_col_name(self, col: int) -> str:
        return self._header[col]

    def get_col_from_name(self, header_string: str) -> int:
        return self._header.index(header_string)


class ProblemItemModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root: QStandardItem = self.invisibleRootItem()

        self.prm_item: QStandardItem = self.append_table_item('prm')
        self.obj_item: QStandardItem = self.append_table_item('obj')
        self.cns_item: QStandardItem = self.append_table_item('cns')
        self.run_item: QStandardItem = self.append_table_item('run')

        self.prm_model: QAbstractTableModel = MyStandardItemAsTableModel(self.prm_item)
        self.obj_model: QAbstractTableModel = MyStandardItemAsTableModel(self.obj_item)
        self.cns_model: QAbstractTableModel = MyStandardItemAsTableModel(self.cns_item)
        self.run_model: QAbstractTableModel = MyStandardItemAsTableModel(self.run_item)

    def append_table_item(self, text) -> QStandardItem:
        table: QStandardItem = QStandardItem(text)
        table.setRowCount(0)
        table.setColumnCount(0)
        self.root.setColumnCount(max(self.root.columnCount(), table.columnCount()))
        self.root.appendRow(table)
        return table


    def load_prm(self):
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
        table = self.prm_item
        table.clearData()
        self.prm_item.setText('prm')
        table.setRowCount(0)
        table.setColumnCount(6)
        self.root.setColumnCount(max(self.root.columnCount(), table.columnCount()))

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
        self.prm_model.beginResetModel()

        # set data to table
        table.setRowCount(len(names))

        self.prm_model.set_header([
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
        self.prm_model.endResetModel()








