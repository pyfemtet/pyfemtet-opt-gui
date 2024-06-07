
from PySide6.QtGui import QStandardItem
from PySide6.QtCore import Qt, QAbstractTableModel



def _isnumeric(exp):
    try:
        float(str(exp))
        isnumeric = True
    except ValueError:
        isnumeric = False
    return isnumeric


class MyStandardItemAsTableModel(QAbstractTableModel):
    def __init__(self, table_item: QStandardItem, root: QStandardItem, parent=None):
        self._item: QStandardItem = table_item  # QStandardItem what has table structure children.
        self._header: list[str] = []
        self._root: QStandardItem = root
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

        if role == Qt.CheckStateRole:
            self.layoutChanged.emit()  # これがないとチェックボックスの変更による enable / disable 切り替えが即時にならない

        return True

    # header relative implementation
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.get_col_name(section)
        return None

    def set_header(self, header: list[str]) -> None:
        self._header = header

    def get_col_name(self, col: int) -> str:
        return self._header[col]

    def get_col_from_name(self, header_string: str) -> int:
        return self._header.index(header_string)

    # get item directory
    def get_item(self, row, col) -> QStandardItem:
        return self._item.child(row, col)
