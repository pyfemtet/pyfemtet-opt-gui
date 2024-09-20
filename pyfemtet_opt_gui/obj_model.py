from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QStandardItem
from PySide6.QtWidgets import QStyledItemDelegate, QComboBox

import pyfemtet_opt_gui._p as _p

from pyfemtet_opt_gui.item_as_model import MyStandardItemAsTableModel, _isnumeric

from pyfemtet_opt_gui.ui.return_code import ReturnCode, should_stop


class ObjTableDelegate(QStyledItemDelegate):

    def __init__(self, model: MyStandardItemAsTableModel):
        super().__init__()
        self._model: MyStandardItemAsTableModel = model

    def createEditor(self, parent, option, index):
        col, row = index.column(), index.row()
        col_name = self._model.get_col_name(col)
        if col_name == '  direction  ':
            # コンボボックスエディタを作成
            comboBox = QComboBox(parent)
            comboBox.addItems(['maximize', 'minimize', 'Set to...'])
            comboBox.setFrame(False)
            return comboBox
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        col, row = index.column(), index.row()
        col_name = self._model.get_col_name(col)
        if col_name == '  direction  ':
            # コンボボックスにデータを設定
            value = index.model().data(index, Qt.EditRole)
            editor.setCurrentText(value)
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        col, row = index.column(), index.row()
        col_name = self._model.get_col_name(col)
        if col_name == '  direction  ':
            # コンボボックスのデータをモデルに設定
            model.setData(index, editor.currentText(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)

    # def paint(self, painter, option, index):
    #     col, row = index.column(), index.row()
    #     col_name = self._model.get_col_name(col)
    #     if col_name == '  direction  ':
    #         # index...proxyindex
    #         # _model...original
    #         value = self._model.get_item(index.row()+1, index.column()).text()
    #         combo = QComboBox()
    #         combo.addItems([value])
    #         combo.setCurrentText(value)
    #         combo.setFrame(False)
    #
    #         painter.save()
    #
    #         painter.translate(option.rect.topLeft())
    #         combo.resize(option.rect.size())
    #         combo.render(painter, QPoint())
    #
    #         painter.restore()
    #     else:
    #         super().paint(painter, option, index)


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
    HEADER = ['use', 'name', '  direction  ', 'set to']  # require margin to paint combobox to objective table, but its resizemode is ResizeToContent so setMargin doesn't work.

    def __init__(self, table_item: QStandardItem, root: QStandardItem, parent=None):
        super().__init__(table_item, root, parent)
        self.initialize_table()

    def initialize_table(self):

        self.beginResetModel()

        # initialize table
        self._item.clearData()
        self._item.setText(self._category)
        self._item.setRowCount(0)
        self._item.setColumnCount(len(self.HEADER))
        self.set_header(self.HEADER)
        self._root.setColumnCount(max(self._root.columnCount(), self._item.columnCount()))

        self.endResetModel()

    def load(self) -> ReturnCode:
        # のちの処理で、ここの順番は Femtet から
        # 取得した目的関数の順番をそのまま使う
        # 前提の部分があるので、現在のデータを
        # 別の形に保存し、目的関数を上書きして
        # から書き戻す

        # if Femtet is not alive, do nothing
        if not _p.check_femtet_alive():
            return ReturnCode.ERROR.FEMTET_CONNECTION_FAILED

        # load objective names
        names = _p.get_parametric_output_names()

        # if no objectives in Femtet, show error message
        if names is None:
            return ReturnCode.WARNING.PARAMETRIC_OUTPUT_EMPTY
        if len(names) == 0:
            return ReturnCode.WARNING.PARAMETRIC_OUTPUT_EMPTY

        # declare
        table: QStandardItem = self._item

        # get current table state
        current_data = self.get_current_table_as_dict()

        # notify to start editing to the abstract model
        self.beginResetModel()

        # initialize
        self.initialize_table()

        # set data to table
        table.setRowCount(len(names)+1)  # including header row (hidden by WithoutHeader proxy).

        for row, name in enumerate(names):

            # use
            item = QStandardItem()
            item.setCheckable(True)
            item.setCheckState(Qt.CheckState.Checked)
            if name in current_data.keys():
                item.setCheckState(current_data[name]['use'])
            table.setChild(row+1, 0, item)

            # name
            item = QStandardItem(name)
            table.setChild(row+1, 1, item)

            # direction
            item = QStandardItem('maximize')
            if name in current_data.keys():
                item = QStandardItem(current_data[name]['direction'])
            table.setChild(row+1, 2, item)

            # set to
            item = QStandardItem('(ignore) 0')
            if name in current_data.keys():
                item = QStandardItem(current_data[name]['set_to'])
            table.setChild(row+1, 3, item)

        # notify to end editing to the abstract model
        self.endResetModel()

        return super().load()

    def flags(self, index):
        if not index.isValid(): return super().flags(index)

        col, row = index.column(), index.row()
        col_name = self.get_col_name(col)

        if col_name == 'set to':
            # if direction is "Maximize" or "Minimize", (set to)+=(ignored) and disable
            dir_col = self.get_col_from_name('  direction  ')
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

        # when direction is changed, change 'Set to...'.
        if col_name == '  direction  ':
            IGNORE_PREFIX = '(ignore) '

            setto_col = self.get_col_from_name('set to')
            setto_index = self.createIndex(row, setto_col)
            setto_value = self.data(setto_index)

            # if direction is "Maximize" or "Minimize,
            # set_to = (ignored) + set_to
            if value in ['minimize', 'maximize']:
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

            dir_col = self.get_col_from_name('  direction  ')
            dir_index = self.createIndex(row, dir_col)
            dir_value = self.data(dir_index)

            if (
                    dir_value == 'Set to...'
                    and not _isnumeric(value)
            ):
                _p.logger.error('数値を入力してください。')
                return False

        # if all of 'use' is unchecked, raise warning
        if (col_name == 'use') and (role == Qt.ItemDataRole.CheckStateRole):
            col2 = self.get_col_from_name('use')
            unchecked = {}
            for row2 in range(1, self.rowCount()):
                unchecked.update(
                    {row2: self.get_item(row2, col2).checkState() == Qt.CheckState.Unchecked}
                )
            unchecked[row] = value == Qt.CheckState.Unchecked.value
            if all(unchecked.values()):
                should_stop(ReturnCode.WARNING.OBJECTIVE_NOT_SELECTED)
                return False

        return super().setData(index, value, role)

    def get_objective_names(self, with_row=False) -> list[str]:
        # get all objective names in model
        out = []
        out1 = []
        table: QStandardItem = self._item
        for r in range(1, table.rowCount()):
            # name
            name = table.child(r, self.get_col_from_name('name')).text()
            out.append(name)
            out1.append(r)
        if with_row:
            return out, out1
        else:
            return out

    def get_current_table_as_dict(self) -> dict:
        out = dict()

        table: QStandardItem = self._item
        for r in range(1, table.rowCount()):
            # name
            name: str = table.child(r, self.get_col_from_name('name')).text()

            # use
            use: Qt.CheckState = table.child(r, self.get_col_from_name('use')).checkState()

            # direction
            direction: str = table.child(r, self.get_col_from_name('  direction  ')).text()

            # set to
            set_to: str = table.child(r, self.get_col_from_name('set to')).text()

            out[name] = dict(
                use=use,
                direction=direction,
                set_to=set_to,
            )

        return out
