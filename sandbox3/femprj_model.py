from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox

import _p

from item_as_model import MyStandardItemAsTableModel, _isnumeric


class FEMPrjModel(MyStandardItemAsTableModel):
    """A table for determining whether to use Femtet variables in optimization.

    use  | item   | value
    ----------------------
    None | femprj | str
    None | model  | str

    # uneditable

    """
    CATEGORY = 'model'
    HEADER = ['use', 'item', 'value']
    ROW_COUNT = 2

    def load(self):
        # initialize table
        table: QStandardItem = self._item
        table.clearData()
        table.setText(self.CATEGORY)
        table.setRowCount(self.ROW_COUNT)
        table.setColumnCount(3)

        self._root.setColumnCount(max(self._root.columnCount(), table.columnCount()))

        # if Femtet is not alive, do nothing
        if not _p.check_femtet_alive():
            _p.logger.warning('Femtet との接続ができていません。')
            return False

        # load value
        prj = _p.Femtet.Project
        model = _p.Femtet.AnalysisModelName

        # TODO: if no prm, show warning dialog
        if prj is None:
            _p.logger.warning('Femtet でプロジェクトが開かれていません。')
            return False
        elif prj == '':
            _p.logger.warning('Femtet でプロジェクトが開かれていません。')
            return False

        # notify to start editing to the abstract model
        self.beginResetModel()

        # set data to table
        self.set_header(self.HEADER)

        # ===== femprj =====
        # use
        item = QStandardItem()
        table.setChild(0, 0, item)
        # item
        item = QStandardItem('femprj')
        table.setChild(0, 1, item)
        # value
        item = QStandardItem(prj)
        table.setChild(0, 2, item)

        # ===== model =====
        # use
        item = QStandardItem()
        table.setChild(1, 0, item)
        # item
        item = QStandardItem('model')
        table.setChild(1, 1, item)
        # value
        item = QStandardItem(model)
        table.setChild(1, 2, item)

        # notify to end editing to the abstract model
        self.endResetModel()

    def flags(self, index):
        if not index.isValid(): return super().flags(index)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        if col_name == 'set to':
            # if direction is "Maximize" or "Minimize", (set to)+=(ignored) and disable
            dir_col = self.get_col_from_name('direction')
            dir_index = self.createIndex(row, dir_col)
            if self.data(dir_index) in ['Minimize', 'Maximize']:
                return ~Qt.ItemIsEnabled

            # elif direction is "Set to...", (set to).replace((ignored), '') and float only
            elif self.data(dir_index) == 'Set to...':
                return super().flags(index)

        # if checkbox is false, disable the row (excluding use column).
        use_col = self.get_col_from_name('use')
        use_item = self.get_item(row, use_col)
        if use_item.checkState() == Qt.CheckState.Unchecked:
            if col_name != 'use':
                return ~Qt.ItemIsEnabled

        # use / name is uneditable
        if col_name in ['use', 'name']:
            flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable
            if col_name == 'use':
                flags = flags | Qt.ItemIsUserCheckable
            return flags

        return super().flags(index)

    def setData(self, index, value, role=Qt.EditRole) -> bool:
        if not index.isValid(): return super().setData(index, value, role)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        if col_name == 'direction':
            IGNORE_PREFIX = '(ignore) '

            setto_col = self.get_col_from_name('set to')
            setto_index = self.createIndex(row, setto_col)
            setto_value = self.data(setto_index)

            # if direction is "Maximize" or "Minimize,
            # set_to = (ignored) + set_to
            if value in ['Minimize', 'Maximize']:
                if IGNORE_PREFIX not in setto_value:
                    setto_value = IGNORE_PREFIX + setto_value
                    super().setData(setto_index, setto_value)

            # if direction is "Set to...",
            # set_to.replace((ignored), '')
            elif value == 'Set to...':
                setto_value = setto_value.replace(IGNORE_PREFIX, '')
                super().setData(setto_index, setto_value)

        # set_to must be numeric if direction is 'Set to...'
        if col_name == 'set to':

            dir_col = self.get_col_from_name('direction')
            dir_index = self.createIndex(row, dir_col)
            dir_value = self.data(dir_index)

            if (
                    dir_value == 'Set to...'
                and not _isnumeric(value)
            ):
                _p.logger.error('数値を入力してください。')
                return False

        return super().setData(index, value, role)
