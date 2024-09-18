from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt, QSortFilterProxyModel

from pyfemtet_opt_gui.prm_model import PrmModel
from pyfemtet_opt_gui.obj_model import ObjModel
from pyfemtet_opt_gui.run_model import RunModel
from pyfemtet_opt_gui.femprj_model import FEMPrjModel


class ProblemItemModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root: QStandardItem = self.invisibleRootItem()

        # standard item
        self.femprj_item: QStandardItem = self.append_table_item('model')
        self.prm_item: QStandardItem = self.append_table_item('parameter')
        self.obj_item: QStandardItem = self.append_table_item('objective')
        # self.cns_item: QStandardItem = self.append_table_item('constraint')
        self.run_item: QStandardItem = self.append_table_item('settings')

        # standard item model to view in tableview
        self.femprj_model: FEMPrjModel = FEMPrjModel(self.femprj_item, self.root)
        self.prm_model: PrmModel = PrmModel(self.prm_item, self.root)
        self.obj_model: ObjModel = ObjModel(self.obj_item, self.root)
        # self.cns_model: QAbstractTableModel = MyStandardItemAsTableModel(self.cns_item)
        self.run_model: RunModel = RunModel(self.run_item, self.root)

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

        # if header row, show anyway (note: femprj_model have no header row but the first row should be shown)
        else:
            if source_row == 0:
                return True

        sourceModel: ProblemItemModel = self.sourceModel()

        # if prm or obj, invisible if non-checkable
        category = source_parent.data()
        if category in ['parameter', 'objective']:
            index = sourceModel.index(source_row, 0, source_parent)
            item: QStandardItem = sourceModel.itemFromIndex(index)
            if not item.isCheckable():
                return False

        # invisible if unchecked
        first_column_index = sourceModel.index(source_row, 0, source_parent)
        first_column_data = first_column_index.data(Qt.ItemDataRole.CheckStateRole)
        if first_column_data == Qt.CheckState.Unchecked.value:
            return False

        # else, show anyway
        return True

    def flags(self, proxyIndex):
        # uneditable anyway
        return Qt.ItemFlag.ItemIsEnabled

    def data(self, proxyIndex, role=Qt.ItemDataRole.DisplayRole):
        sourceIndex = self.mapToSource(proxyIndex)
        sourceModel: ProblemItemModel = self.sourceModel()
        item = sourceModel.itemFromIndex(sourceIndex)

        # invisible checkbox
        if item.isCheckable():
            return None

        # invisible header item 'use'
        if item.text() == 'use':
            return None

        # invisible item its header is 'test'
        is_prm_model = sourceIndex.parent().data() == sourceModel.prm_item.text()
        is_test_column = sourceIndex.column() == sourceModel.prm_model.get_col_from_name(sourceModel.prm_model.TEST)
        if is_prm_model and is_test_column:
            return None

        # bold if header row
        for __ in range(1):  # dummy loop to use if-break

            if (sourceIndex.row() == 0) and (sourceIndex.column() > 0):

                # only femprj_model have no header row
                if sourceIndex.parent().data() == sourceModel.femprj_item.text():
                    break

                if role == Qt.ItemDataRole.FontRole:
                    font = QFont()
                    font.setBold(True)
                    font.setItalic(True)
                    return font

        # invisible if contains (ignore)
        if '(ignore)' in item.text():
            return None

        # if all objectives set to (ignore), hide 'set to'
        if item.text() == 'set to':
            if role == Qt.ItemDataRole.DisplayRole:
                unused = []
                col = sourceModel.obj_model.get_col_from_name('set to')
                for row in range(1, sourceModel.obj_model.rowCount()):
                    unused.append('(ignore)' in sourceModel.obj_model.get_item(row, col).text())
                if all(unused):
                    return None

        # alignment
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        return super().data(proxyIndex, role)
