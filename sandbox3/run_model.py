from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox

from item_as_model import MyStandardItemAsTableModel, _isnumeric

import _p  # for logger


class RunTableDelegate(QStyledItemDelegate):

    def __init__(self, model: MyStandardItemAsTableModel):
        super().__init__()
        self._model: MyStandardItemAsTableModel = model

    def createEditor(self, parent, option, index):
        # col, row = index.column(), index.row()
        # col_name = self._model.get_col_name(col)
        # if col_name == 'direction':
        #     # コンボボックスエディタを作成
        #     comboBox = QComboBox(parent)
        #     comboBox.addItems(['Maximize', 'Minimize', 'Set to...'])
        #     return comboBox
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        # col, row = index.column(), index.row()
        # col_name = self._model.get_col_name(col)
        # if col_name == 'direction':
        #     # コンボボックスにデータを設定
        #     value = index.model().data(index, Qt.EditRole)
        #     editor.setCurrentText(value)
        # else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        # col, row = index.column(), index.row()
        # col_name = self._model.get_col_name(col)
        # if col_name == 'direction':
        #     # コンボボックスのデータをモデルに設定
        #     model.setData(index, editor.currentText(), Qt.EditRole)
        # else:
            super().setModelData(editor, model, index)


class RunModel(MyStandardItemAsTableModel):
    """A table to set arguments for FEMOpt.optimize().

    use              | item         | value
    ----------------------------------------------
    checkbox         | n_trial      | 10 (positive int only)
    checkbox         | timeout      | 10 (minutes, positive int only)
    None             | n_parallel   | 1 (positive int only)

    # if both n_trial and timeout are Unchecked, show warning.
    # use and item are uneditable.
    # if Uncheckable, the row is disabled excluding use column.

    """
    CATEGORY = 'optimization setting'
    HEADER = ['use', 'item', 'value']
    ROW_COUNT = 3

    def __init__(self, table_item: QStandardItem, root: QStandardItem, parent=None):
        super().__init__(table_item=table_item, root=root, parent=parent)

        # initialize table
        table: QStandardItem = self._item
        table.clearData()
        table.setText(self.CATEGORY)
        table.setRowCount(self.ROW_COUNT)
        table.setColumnCount(3)

        # extend root column if needed.
        self._root.setColumnCount(max(self._root.columnCount(), table.columnCount()))

        # notify to start editing to the abstract model
        self.beginResetModel()

        # set data to table
        table.setRowCount(self.ROW_COUNT)
        self.set_header(self.HEADER)

        # ===== n_trial =====
        # use
        item = QStandardItem()
        item.setCheckable(True)
        item.setCheckState(Qt.CheckState.Unchecked)
        table.setChild(0, 0, item)
        # item
        item = QStandardItem('solve number')
        table.setChild(0, 1, item)
        # value
        item = QStandardItem('10')
        table.setChild(0, 2, item)

        # ===== timeout =====
        # use
        item = QStandardItem()
        item.setCheckable(True)
        item.setCheckState(Qt.CheckState.Unchecked)
        table.setChild(1, 0, item)
        # item
        item = QStandardItem('timeout(min)')
        table.setChild(1, 1, item)
        # value
        item = QStandardItem('3')
        table.setChild(1, 2, item)

        # ===== n_parallel =====
        # use
        item = QStandardItem()
        table.setChild(2, 0, item)
        # item
        item = QStandardItem('use license number')
        table.setChild(2, 1, item)
        # value
        item = QStandardItem('1')
        table.setChild(2, 2, item)

        # notify to end editing to the abstract model
        self.endResetModel()

    def get_item_name(self, row) -> str:
        col = self.get_col_from_name('item')
        return self.get_item(row, col).text()

    def flags(self, index):
        if not index.isValid(): return super().flags(index)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        # use is checkable
        if col_name == 'use':
            return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable

        # if checkbox is false, disable the row (excluding use column).
        item_name = self.get_item_name(row)
        if item_name in ['solve number', 'timeout(min)']:
            use_col = self.get_col_from_name('use')
            use_item = self.get_item(row, use_col)
            if use_item.checkState() == Qt.CheckState.Unchecked:
                if col_name != 'use':
                    return ~Qt.ItemFlag.ItemIsEnabled

        # item is uneditable
        if col_name == 'item':
            return Qt.ItemFlag.ItemIsEnabled

        return super().flags(index)

    def setData(self, index, value, role=Qt.EditRole) -> bool:
        if not index.isValid(): return super().setData(index, value, role)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        # set_to must be numeric if direction is 'Set to...'
        if col_name == 'value':

            name_col = self.get_col_from_name('item')
            name_index = self.createIndex(row, name_col)
            name_value = self.data(name_index)

            if name_value == 'solve number':
                raise_alert = False

                if not _isnumeric(value):
                    raise_alert = True
                else:
                    if float(value) != int(value):
                        raise_alert = True
                    else:
                        if int(value) <= 0:
                            raise_alert = True

                if raise_alert:
                    _p.logger.error('自然数を入力してください。')
                    return False

            if name_value == 'use license number':
                raise_alert = False

                if not _isnumeric(value):
                    raise_alert = True
                else:
                    if float(value) != int(value):
                        raise_alert = True
                    else:
                        if int(value) <= 0:
                            raise_alert = True

                if raise_alert:
                    _p.logger.error('自然数を入力してください。')
                    return False

            if name_value == 'timeout(min)':
                raise_alert = False

                if not _isnumeric(value):
                    raise_alert = True
                else:
                    if float(value) <= 0:
                        raise_alert = True

                if raise_alert:
                    _p.logger.error('正の数を入力してください。')
                    return False

        return super().setData(index, value, role)
