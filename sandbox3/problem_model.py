from PySide6.QtGui import QStandardItemModel, QStandardItem

from prm_model import PrmModel



class ProblemItemModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root: QStandardItem = self.invisibleRootItem()

        self.prm_item: QStandardItem = self.append_table_item('prm')
        self.obj_item: QStandardItem = self.append_table_item('obj')
        self.cns_item: QStandardItem = self.append_table_item('cns')
        self.run_item: QStandardItem = self.append_table_item('run')

        self.prm_model: PrmModel = PrmModel(self.prm_item, self.root)
        # self.obj_model: QAbstractTableModel = MyStandardItemAsTableModel(self.obj_item)
        # self.cns_model: QAbstractTableModel = MyStandardItemAsTableModel(self.cns_item)
        # self.run_model: QAbstractTableModel = MyStandardItemAsTableModel(self.run_item)

    def append_table_item(self, text) -> QStandardItem:
        table: QStandardItem = QStandardItem(text)
        table.setRowCount(0)
        table.setColumnCount(0)
        self.root.setColumnCount(max(self.root.columnCount(), table.columnCount()))
        self.root.appendRow(table)
        return table

