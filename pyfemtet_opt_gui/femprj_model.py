from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox

import pyfemtet_opt_gui._p as _p

from pyfemtet_opt_gui.item_as_model import MyStandardItemAsTableModel, _isnumeric
from pyfemtet_opt_gui.ui.return_code import ReturnCode


class FEMPrjModel(MyStandardItemAsTableModel):
    """A table for determining whether to use Femtet variables in optimization.

    use  | item   | value
    ----------------------
    None | femprj | str
    None | model  | str

    # uneditable
    # use column is a dummy column

    """
    HEADER = ['use', 'key', 'value']
    ROW_COUNT = 2

    def __init__(self, table_item: QStandardItem, root: QStandardItem, parent=None):
        super().__init__(table_item, root, parent)
        self.initialize_table()

    def initialize_table(self):
        # initialize table
        self._item.clearData()
        self._item.setText(self._category)
        self._item.setRowCount(self.ROW_COUNT)
        self._item.setColumnCount(3)
        self.set_header(self.HEADER)
        self._root.setColumnCount(max(self._root.columnCount(), self._item.columnCount()))

    def load(self) -> ReturnCode:
        """setChild starts with row=0 because this model have no need to show via WithoutHeader proxy model."""

        self.initialize_table()

        # if Femtet is not alive, do nothing
        if not _p.check_femtet_alive():
            # _p.logger.warning('Femtet との接続ができていません。')
            return ReturnCode.ERROR.FEMTET_NOT_FOUND

        # load value
        prj = _p.Femtet.Project
        model = _p.Femtet.AnalysisModelName
        if prj is None:
            ret_code = ReturnCode.ERROR.FEMTET_NO_PROJECT
        elif prj == '':
            ret_code = ReturnCode.ERROR.FEMTET_NO_PROJECT
        else:
            ret_code = ReturnCode.INFO.SUCCEED

        if ret_code == ReturnCode.ERROR.FEMTET_NO_PROJECT:
            prj, model = '', ''

        # notify to start editing to the abstract model
        self.beginResetModel()

        # ===== femprj =====
        # setChild starts with row=0 so header row is overwritten
        # use
        item = QStandardItem()
        self._item.setChild(0, 0, item)
        # item
        item = QStandardItem('femprj')
        self._item.setChild(0, 1, item)
        # value
        item = QStandardItem(prj)
        self._item.setChild(0, 2, item)

        # ===== model =====
        # use
        item = QStandardItem()
        self._item.setChild(1, 0, item)
        # item
        item = QStandardItem('model')
        self._item.setChild(1, 1, item)
        # value
        item = QStandardItem(model)
        self._item.setChild(1, 2, item)

        # notify to end editing to the abstract model
        self.endResetModel()

        return ret_code

    def get_femprj(self):
        femprj_item = self.get_item(0, 2)
        model_item = self.get_item(1, 2)
        if femprj_item is None or model_item is None:
            return '', ''
        else:
            return femprj_item.text(), model_item.text()
