# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

from pyfemtet_opt_gui_2.common.qt_util import *

import enum
from typing import Any


__all__ = [
    'CommonItemColumnName',
    'StandardItemModelWithoutFirstRow',
    'StandardItemModelWithEnhancedFirstRow',
    'StandardItemModelAsQStandardItem',
    'StandardItemModelWithHeader',
]

ICON_PATH = r'pyfemtet-opt-gui\pyfemtet_opt_gui_2\assets\icon\arrow.svg'


# pyfemtet.opt で使う Item の共通部分の列挙体
class CommonItemColumnName(enum.StrEnum):
    use = '使用'
    name = '名前'


class StandardItemModelWithHeader(StandardItemModelWithHeaderSearch):

    ColumnNames = CommonItemColumnName

    def __init__(self, parent=None, _with_dummy=True):
        super().__init__(parent)

        self.setup_header_data(self.ColumnNames)
        if _with_dummy:
            self._set_dummy_data()

    def setup_header_data(self, HeaderNames: type[enum.StrEnum]):
        with EditModel(self):
            self.setColumnCount(len(HeaderNames))
            for c, name in enumerate(HeaderNames):
                # displayData
                self.setHeaderData(
                    _section := c,
                    _orientation := Qt.Orientation.Horizontal,
                    _value := name,
                    _role := Qt.ItemDataRole.DisplayRole
                )
                # headerData
                self.setHeaderData(
                    _section := c,
                    _orientation := Qt.Orientation.Horizontal,
                    _value := name,
                    _role := Qt.ItemDataRole.UserRole,
                )

            # first row == header row for treeview
            # likely to same as displayData
            self.setRowCount(1)
            for c, name in enumerate(HeaderNames):
                item = QStandardItem()
                item.setText(name)
                self.setItem(0, c, item)

    def set_data_from_stash(self, item, name, header_data, stashed_data):
        data: dict[Qt.ItemDataRole, Any] = stashed_data[name][header_data]
        for role, value in data.items():
            item.setData(value, role)

    def stash_current_table(self) -> dict[str, dict[str, dict[Qt.ItemDataRole, Any]]]:
        """load 時に既存のデータを上書きする為に stash する

        dict[name, dict[ColumnName, dict[Qt.ItemDataRole, Any]]

        """

        out = dict()

        # 既存データについて iteration
        for r in range(1, self.rowCount()):

            # 行ごとに dict を作成, key は obj_name など
            row_information = dict()

            # 列ごとにデータを収取
            for header_name in self.ColumnNames:
                c = self.get_column_by_header_data(header_name)
                index = self.index(r, c)
                data = self.itemData(index)
                row_information.update({header_name: data})

            # データを収集出来たら obj_name をキーにして
            # out に追加
            c = self.get_column_by_header_data(self.ColumnNames.name)
            out.update({self.item(r, c).text(): row_information})

        return out

    def _set_dummy_data(self):
        rows = 3
        columns = len(self.ColumnNames)

        with EditModel(self):
            self.setRowCount(rows + 1)  # header row for treeview

            # table
            for r in range(1, rows+1):
                for c in range(columns):
                    item = QStandardItem()
                    # NOTE: The default implementation treats Qt::EditRole and Qt::DisplayRole as referring to the same data.
                    # item.setData(f'text{r}{c}', role=Qt.ItemDataRole.EditRole)
                    item.setData(f'text{r}{c}', role=Qt.ItemDataRole.DisplayRole)
                    item.setData(f'tooltip of {r}{c}', role=Qt.ItemDataRole.ToolTipRole)
                    item.setData(f'WhatsThis of {r}{c}', role=Qt.ItemDataRole.WhatsThisRole)
                    # item.setData(QSize(w=10, h=19), role=Qt.ItemDataRole.SizeHintRole)  # 悪い
                    item.setData(f'internal_text{r}{c}', role=Qt.ItemDataRole.UserRole)
                    # item.setText(f'text{r}{c}')

                    if c == 1 or c == 2:
                        icon = QIcon(ICON_PATH)  # Cannot read .ico file, but can .svg file?
                        item.setIcon(icon)

                    if c == 0 or c == 2:
                        item.setCheckable(True)
                        item.setCheckState(Qt.CheckState.Checked)

                    if c == 2:
                        # current_text = item.text()
                        current_text = item.data(Qt.ItemDataRole.DisplayRole)
                        item.setText(current_text + '\n2 line')

                    self.setItem(r, c, item)


# 各ページで使う、一行目を隠す ProxyModel
class StandardItemModelWithoutFirstRow(SortFilterProxyModelOfStandardItemModel):
    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        if source_row == 0:
            return False
        return True


# 一覧ページで使う、各モデルの一行目を強調する QStandardItemModel
class StandardItemModelWithEnhancedFirstRow(StandardItemModelWithHeaderSearch):

    def data(self, index, role=...):

        is_submodel = index.parent().isValid()

        if is_submodel:
            if (index.row() == 0) and (role == Qt.ItemDataRole.FontRole):
                return get_enhanced_font()
            if (index.row() == 0) and (role == Qt.ItemDataRole.BackgroundRole):
                default_color = QApplication.palette().color(QPalette.ColorRole.Base)
                return default_color.darker(120)

        return super().data(index, role)


# QStandardItem を StandardItemModel に変換するクラス
# 各 StandardItem を各ページの TableView に表示するために使う
class StandardItemModelAsQStandardItem(QStandardItem):

    source_model: StandardItemModelWithHeaderSearch
    proxy_model: SortFilterProxyModelOfStandardItemModel

    def __init__(
            self,
            text: str,
            model: StandardItemModelWithHeaderSearch | SortFilterProxyModelOfStandardItemModel
    ):
        if isinstance(model, StandardItemModelWithHeaderSearch):
            self.source_model = model
            self.proxy_model = SortFilterProxyModelOfStandardItemModel()
            self.proxy_model.setSourceModel(model)
        elif isinstance(model, SortFilterProxyModelOfStandardItemModel):
            self.source_model = model.sourceModel()
            self.proxy_model = model
        else:
            raise NotImplementedError

        super().__init__(self.proxy_model.rowCount(), self.proxy_model.columnCount())
        self.setText(text)
        self.do_clone_all()
        self.proxy_model.dataChanged.connect(self.do_clone)

    def do_clone_all(self):
        indices = []
        for r in range(self.proxy_model.rowCount()):
            for c in range(self.proxy_model.columnCount()):
                indices.append(self.proxy_model.index(r, c))
        self.do_clone(*indices)

    def do_clone(self, *args):
        for arg in args:
            if isinstance(arg, QModelIndex):
                data = self.proxy_model.itemData(arg)
                item = QStandardItem()
                for role, value in data.items():
                    item.setData(value, role)
                r, c = arg.row(), arg.column()
                self.setChild(r, c, item)
