from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox

import _p

from item_as_model import MyStandardItemAsTableModel, _isnumeric
from pyfemtet_opt_gui.ui.return_code import ReturnCode


class ObjTableDelegate(QStyledItemDelegate):

    def __init__(self, model: MyStandardItemAsTableModel):
        super().__init__()
        self._model: MyStandardItemAsTableModel = model

    def createEditor(self, parent, option, index):
        col, row = index.column(), index.row()
        col_name = self._model.get_col_name(col)
        if col_name == 'direction':
            # コンボボックスエディタを作成
            comboBox = QComboBox(parent)
            comboBox.addItems(['maximize', 'minimize', 'Set to...'])
            return comboBox
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        col, row = index.column(), index.row()
        col_name = self._model.get_col_name(col)
        if col_name == 'direction':
            # コンボボックスにデータを設定
            value = index.model().data(index, Qt.EditRole)
            editor.setCurrentText(value)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        col, row = index.column(), index.row()
        col_name = self._model.get_col_name(col)
        if col_name == 'direction':
            # コンボボックスのデータをモデルに設定
            model.setData(index, editor.currentText(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)


class ObjModel(MyStandardItemAsTableModel):
    """A table for determining whether to use Femtet variables in optimization.

    use        | name       | direction   | set to
    ----------------------------------------------
    checkbox   | str        | combobox    | float or empty
    uneditable | uneditable

    # if checkbox is false, disable the row (excluding use column).
    # if direction is "Maximize" or "Minimize", (set to)+=(ignored) and disable
    # elif direction is "Set to...", (set to).replace((ignored), '') and float only
    # use / name is uneditable

    """
    HEADER = ['use', 'name', 'direction', 'set to']

    def load(self) -> ReturnCode:
        # initialize table
        self._item.clearData()
        self._item.setText(self._category)
        self._item.setRowCount(0)
        self._item.setColumnCount(len(self.HEADER))
        self.set_header(self.HEADER)
        self._root.setColumnCount(max(self._root.columnCount(), self._item.columnCount()))

        # if Femtet is not alive, do nothing
        if not _p.check_femtet_alive():
            return ReturnCode.ERROR.FEMTET_CONNECTION_FAILED

        # load prm
        names = _p.get_parametric_output_names()

        if names is None:
            return ReturnCode.WARNING.PARAMETRIC_OUTPUT_EMPTY

        if len(names) == 0:
            return ReturnCode.WARNING.PARAMETRIC_OUTPUT_EMPTY

        # notify to start editing to the abstract model
        self.beginResetModel()

        # set data to table
        self._item.setRowCount(len(names)+1)  # including header row (hidden by WithoutHeader proxy).

        for row, name in enumerate(names):
            # use
            item = QStandardItem()
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Checked)
            self._item.setChild(row+1, 0, item)

            # name
            item = QStandardItem(name)
            self._item.setChild(row+1, 1, item)

            # direction
            item = QStandardItem('maximize')  # TODO: load if previous setting exists
            self._item.setChild(row+1, 2, item)

            # set to
            item = QStandardItem('(ignore) 0')
            self._item.setChild(row+1, 3, item)

        # notify to end editing to the abstract model
        self.endResetModel()

        return super().load()

    def flags(self, index):
        if not index.isValid(): return super().flags(index)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        if col_name == 'set to':
            # if direction is "Maximize" or "Minimize", (set to)+=(ignored) and disable
            dir_col = self.get_col_from_name('direction')
            dir_index = self.createIndex(row, dir_col)
            if self.data(dir_index) in ['minimize', 'maximize']:
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

    def check_use_any(self):
        col = self.get_col_from_name('use')
        used = []
        for row in range(1, self.rowCount()):
            index = self.createIndex(row, col)
            used.append(self.data(index, Qt.ItemDataRole.CheckStateRole))
        return any(used)
