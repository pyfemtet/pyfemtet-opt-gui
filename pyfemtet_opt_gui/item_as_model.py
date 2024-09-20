from PySide6.QtGui import QStandardItem
from PySide6.QtCore import Qt, QAbstractTableModel, QSortFilterProxyModel

from pyfemtet_opt_gui.ui.return_code import ReturnCode


def _isnumeric(exp):
    try:
        float(str(exp))
        isnumeric = True
    except ValueError:
        isnumeric = False
    return isnumeric


class MyStandardItemAsTableModel(QAbstractTableModel):

    HEADER = []

    def __init__(self, table_item: QStandardItem, root: QStandardItem, parent=None):
        self._item: QStandardItem = table_item  # QStandardItem what has table structure children.
        self._header: list[str] = self.HEADER
        self._root: QStandardItem = root
        self._category: str = self._item.text()
        super().__init__(parent)

    def load(self) -> ReturnCode:
        """setChild must be starts with row=1."""
        return ReturnCode.INFO.SUCCEED

    def rowCount(self, parent=None): return self._item.rowCount()
    def columnCount(self, parent=None): return self._item.columnCount()
    # def insertRow(self, row, parent = ...):  # TODO: implement CnsModel.add_row() by correct way.

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

        self.beginResetModel()
        self.dataChanged.emit(self.createIndex(row, col), self.createIndex(row, col))
        self.endResetModel()

        return True

    # header relative implementation
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.get_col_name(section)
        return None

    def set_header(self, header: list[str]) -> None:
        self._header = header
        for col, h in enumerate(header):
            item = QStandardItem(h)
            self._item.setChild(0, col, item)

    def get_col_name(self, col: int) -> str:
        return self._header[col]

    def get_col_from_name(self, header_string: str) -> int:
        return self._header.index(header_string)

    # get item directory
    def get_item(self, row, col) -> QStandardItem:
        return self._item.child(row, col)


class MyStandardItemAsTableModelWithoutHeader(QSortFilterProxyModel):
    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        if source_row == 0:
            return False
        return True

    def get_col_name(self, col: int) -> str:
        return self.sourceModel().get_col_name(col)

    def get_col_from_name(self, header_string: str) -> int:
        return self.sourceModel().get_col_from_name(header_string)

    # get item directory
    def get_item(self, row, col) -> QStandardItem:
        return self.sourceModel().get_item(row, col)
