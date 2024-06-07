"""Set the table (QStandardItem) what is a part of a tree (QStandardItemModel) to QTableView."""
import sys

from PySide6.QtWidgets import (QApplication, QTreeView, QTableView)

from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtCore import Qt, QAbstractTableModel


class MyStandardItemAsTableModel(QAbstractTableModel):
    def __init__(self, table_item: QStandardItem, parent=None):
        self._item: QStandardItem = table_item  # QStandardItem what has table structure children.
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


def setup_table_item() -> QStandardItem:
    table_item1: QStandardItem = QStandardItem('table item 1')
    table_item1.setRowCount(3); table_item1.setColumnCount(2)
    for row in range(table_item1.rowCount()):
        for col in range(table_item1.columnCount()):
            item = QStandardItem(f'item ({row}, {col})')
            table_item1.setChild(row, col, item)
    return table_item1


# def setup_table_model(parent) -> QStandardItemModel:
#     table_model: QStandardItemModel = QStandardItemModel(parent=parent)
#     for row in range(2):
#         for col in range(2):
#             item = QStandardItem(f'table item ({row}, {col})')
#             table_model.setItem(row, col, item)
#     return table_model


def setup_tree_model() -> QStandardItemModel:
    tree_model: QStandardItemModel = QStandardItemModel()
    root: QStandardItem = tree_model.invisibleRootItem()

    item1 = QStandardItem('top item 1')
    item2 = setup_table_item()
    item3 = QStandardItem('top item 3')

    root.appendRow(item1)
    root.appendRow(item2)
    root.appendRow(item3)

    # setup_table_model(parent=item3)  # ERROR on QStandardItemModel.__init()__

    root.setColumnCount(3)  # これがないと子のカラムデータが表示されない

    return tree_model, item2


if __name__ == '__main__':
    app = QApplication(sys.argv)

    _tree_view = QTreeView()
    _tree_model, _table_item = setup_tree_model()
    _tree_view.setModel(_tree_model)
    _tree_view.show()  # ビューの表示

    _table_view = QTableView()
    # _table_model = QStandardItemModel(3, 2)
    # for row in range(3):
    #     for col in range(2):
    #         item = _table_item.child(row, col)
    #         # _table_model.setItem(row, col, item)  # NG, no item is shown in tableview
    #         _table_model.setItem(row, col, QStandardItem(item))  # OK, but this is a copy of item. That is, a change int one view is not refer to another view.
    _table_model = MyStandardItemAsTableModel(_table_item)
    _table_view.setModel(_table_model)
    _table_view.show()

    sys.exit(app.exec())  # アプリケーションの実行

