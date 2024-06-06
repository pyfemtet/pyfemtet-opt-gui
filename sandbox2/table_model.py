from typing import Optional

import PySide6

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt, QAbstractTableModel, QModelIndex)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHeaderView, QLabel, QPlainTextEdit,
    QPushButton, QSizePolicy, QTableView, QTextEdit,
    QWidget, QWizard, QWizardPage)
import sys
from PySide6.QtWidgets import (
    QApplication, QTableView, QItemDelegate, QComboBox, QSpinBox
)
from PySide6.QtCore import QAbstractTableModel, Qt, QModelIndex, QObject

import _p


def _isnumeric(exp):
    try:
        float(str(exp))
        isnumeric = True
    except ValueError:
        isnumeric = False
    return isnumeric


class BasicTableModel(QAbstractTableModel):
    """1列目がチェックボックスで、既定の動作が Editable な表"""
    def __init__(self, parent: Optional[PySide6.QtCore.QObject] = None):
        self._data = [[]]
        self.columns = []
        super().__init__(parent)

    def get_column(self, col):
        return self.columns[col]

    def rowCount(self, parent = ...):  # QModelIndex()
        return len(self._data)

    def columnCount(self, parent = ...):
        return len(self._data[0])

    def headerData(self, section: int, orientation: PySide6.QtCore.Qt.Orientation, role: int = ...):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.columns[section]
        return None

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DisplayRole or role == Qt.EditRole:
            # 表示または編集時にデータを返す
            return self._data[index.row()][index.column()]

        if role == Qt.CheckStateRole and index.column() == 0:
            # チェックボックスの状態を返す
            return Qt.Checked if self._data[index.row()][index.column()] else Qt.Unchecked

        return None

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        if role == Qt.EditRole:
            # 編集時にデータを設定
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True

        if role == Qt.CheckStateRole and index.column() == 0:
            # チェックボックスの状態を設定
            self._data[index.row()][index.column()] = True if value == Qt.CheckState.Checked.value else False
            self.dataChanged.emit(index, index, [Qt.CheckStateRole])
            self.layoutChanged.emit()  # これがないとチェックボックスの変更による enable / disable 切り替えが即時にならない
            return True

        return False

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


class PrmTableModel(BasicTableModel):
    """A table for determining whether to use Femtet variables in optimization.

    use      | name | expression   | lb             | ub             | test
    --------------------------------------------------------------------------
    checkbox | str  | float or str | float or empty | float or empty | float

    """
    def __init__(self):
        super().__init__()
        self.columns = ['use', 'name', 'expression', 'lb', 'ub', 'test']
        self.load_data()

    def load_data(self):
        data = []

        # if Femtet is not alive, do nothing
        if not _p.check_femtet_alive():
            _p.logger.info('Femtet process is not connected.')
            return False

        # load prm
        from logging import DEBUG
        _p.logger.setLevel(DEBUG)
        names = _p.Femtet.GetVariableNames_py()
        _p.logger.debug(f'names is ({names})')

        # if no prm, show dialog
        if len(names) == 0:
            # TODO: show dialog
            _p.logger.warning('Femtet で変数を設定してください。')
            return False

        # update self._data
        for name in names:
            exp = str(_p.Femtet.GetVariableExpression(name))
            use = _isnumeric(exp)
            value = float(exp) if _isnumeric(exp) else None
            row_data = [use, name, exp, '0.0', '1.0', value]  # TODO: implement delegate
            data.append(row_data)
        self._data = data

        # notify model data updated
        tl = self.createIndex(0, 0)
        br = self.createIndex(5, len(names)-1)
        self.dataChanged.emit(tl, br)

    def flags(self, index):
        row, col = index.row(), index.column()
        col_name = self.get_column(col)

        # 行全体について、exp が数値でなければ disable
        if not _isnumeric(self._data[row][2]):
            return ~Qt.ItemIsEnabled

        # 行全体について、use が True でなければ 2 列目以降 disable
        if not self._data[row][0]:
            if col_name != 'use':
                return ~Qt.ItemIsEnabled

        # チェックボックス列
        if col_name == 'use':
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

        # 編集不可の文字列列
        elif col_name == 'name':
            return Qt.ItemIsEnabled

        # その他
        return super().flags(index)


class ObjTableModel(BasicTableModel):
    """A table for determining whether to use Femtet variables in optimization.

    use      | name | direction   | value
    ----------------------------------------------
    checkbox | str  | combobox    | float or empty

    """
    def __init__(self):
        super().__init__()
        self.columns = ['use', 'name', 'direction', 'value']
        self.load_data()

    def load_data(self):
        # if Femtet is not alive, do nothing
        if not _p.check_femtet_alive():
            _p.logger.info('Femtet process is not connected.')
            return False

        # load obj
        data = []
        names = _p.get_parametric_output_names()
        for name in names:
            row_data = [True, name, 'Maximize', None]  # TODO: implement delegate
            data.append(row_data)
        self._data = data

        # notify model changed
        tl = self.createIndex(0, 0)
        br = self.createIndex(3, len(names)-1)
        self.dataChanged.emit(tl, br)

    def flags(self, index):
        row, col = index.row(), index.column()
        col_name = self.get_column(col)

        # value について、direction が Specify でなければ disable
        if col_name == 'value':
            if self._data[row][2] != 'Specify':
                return ~Qt.ItemIsEnabled

        # use が True でなければ 2 列目以降 disable
        if not self._data[row][0]:
            if col_name != 'use':
                return ~Qt.ItemIsEnabled

        # チェックボックス列
        if col_name == 'use':
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsUserCheckable

        # 編集不可の文字列列
        elif col_name == 'name':
            return Qt.ItemIsEnabled

        # その他
        return super().flags(index)


class ComboBoxDelegate(QItemDelegate):

    def __init__(self, model):
        super().__init__()
        self._model = model

    def createEditor(self, parent, option, index):
        col, row = index.column(), index.row()
        col_name = self._model.get_column(col)
        if col_name == 'direction':
            # コンボボックスエディタを作成
            comboBox = QComboBox(parent)
            comboBox.addItems(['Maximize', 'Minimize', 'Specify'])
            return comboBox
        # elif col_name == 'value':
        #     # スピンボックスエディタを作成
        #     spinBox = QSpinBox(parent)
        #     spinBox.setRange(0, 100)
        #     return spinBox
        return super().createEditor(parent, option, index)

    def setEditorData(self, editor, index):
        col, row = index.column(), index.row()
        col_name = self._model.get_column(col)
        if col_name == 'direction':
            # コンボボックスにデータを設定
            value = index.model().data(index, Qt.EditRole)
            editor.setCurrentText(value)
        # elif col_name == 'value':
        #     # スピンボックスにデータを設定
        #     value = index.model().data(index, Qt.EditRole)
        #     editor.setValue(float(value))
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        col, row = index.column(), index.row()
        col_name = self._model.get_column(col)
        if col_name == 'direction':
            # コンボボックスのデータをモデルに設定
            model.setData(index, editor.currentText(), Qt.EditRole)
        # elif col_name == 'value':
        #     # スピンボックスのデータをモデルに設定
        #     model.setData(index, editor.value(), Qt.EditRole)
        else:
            super().setModelData(editor, model, index)


# これを使いたければ QtDesigner にカスタムとして登録したほうがよい
class SingleClickTableView(QTableView):
    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if index.isValid() and index.column() == 1:
            self.edit(index)
        super(SingleClickTableView, self).mousePressEvent(event)

