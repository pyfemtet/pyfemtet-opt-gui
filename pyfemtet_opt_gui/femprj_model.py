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
