from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QSortFilterProxyModel

from prm_model import PrmModel
from obj_model import ObjModel



class ProblemItemModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root: QStandardItem = self.invisibleRootItem()

        self.prm_item: QStandardItem = self.append_table_item('prm')
        self.obj_item: QStandardItem = self.append_table_item('obj')
        self.cns_item: QStandardItem = self.append_table_item('cns')
        self.run_item: QStandardItem = self.append_table_item('run')

        self.prm_model: PrmModel = PrmModel(self.prm_item, self.root)
        self.obj_model: ObjModel = ObjModel(self.obj_item, self.root)
        # self.cns_model: QAbstractTableModel = MyStandardItemAsTableModel(self.cns_item)
        # self.run_model: QAbstractTableModel = MyStandardItemAsTableModel(self.run_item)

    def append_table_item(self, text) -> QStandardItem:
        table: QStandardItem = QStandardItem(text)
        table.setRowCount(0)
        table.setColumnCount(0)
        self.root.setColumnCount(max(self.root.columnCount(), table.columnCount()))
        self.root.appendRow(table)
        return table


class CustomProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.autoAcceptChildRows = True
        self.recursiveFilteringEnabled = True

    def filterAcceptsRow(self, source_row, source_parent):

        # if top level item, show anyway
        if not source_parent.isValid():
            return True

        # if prm or obj, invisible if unchecked
        category = source_parent.data()
        if category in ['prm', 'objective']:
            index = self.sourceModel().index(source_row, 0, source_parent)
            data = index.data(Qt.CheckStateRole)
            if data == Qt.CheckState.Unchecked.value:
                return False

        # else, show anyway
        return True

    def flags(self, index):
        # uneditable anyway
        return Qt.ItemIsEnabled
