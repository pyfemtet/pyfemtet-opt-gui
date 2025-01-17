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


# QStandardItemModel に自動でクラスメンバーに応じた
# header data をつけるためのクラス
class StandardItemModelWithHeader(StandardItemModelWithHeaderSearch):
    with_first_row = True  # True なら一行目を header と同じにする
    ColumnNames = CommonItemColumnName
    RowNames = None

    def __init__(self, parent=None, _with_dummy=True, with_first_row=True):
        super().__init__(parent)

        self.with_first_row = with_first_row
        self.setup_header_data()
        self.setup_vertical_header_data()

        if _with_dummy:
            self._set_dummy_data()

    def setup_header_data(self):

        HeaderNames = self.ColumnNames

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

            if self.with_first_row:
                # first row == header row for treeview
                # likely to same as displayData
                self.setRowCount(1)
                for c, name in enumerate(HeaderNames):
                    item = QStandardItem()
                    item.setText(name)
                    self.setItem(0, c, item)

    def setup_vertical_header_data(self):

        if self.RowNames is None:
            return

        HeaderNames = self.RowNames

        if self.with_first_row:
            start = 1
            row = len(HeaderNames) + 1
        else:
            start = 0
            row = len(HeaderNames)

        with EditModel(self):
            self.setRowCount(row)
            for r, name in zip(range(start, row), HeaderNames):
                # headerData
                self.setHeaderData(
                    _section := r,
                    _orientation := Qt.Orientation.Vertical,
                    _value := name,
                    _role := Qt.ItemDataRole.UserRole,
                )

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

            # データを収集出来たら obj_name などをキーにして
            # out に追加
            if hasattr(self.ColumnNames, 'name'):
                c = self.get_column_by_header_data(self.ColumnNames.name)
                key = self.item(r, c).text()

            # ColumnNames に name というメンバーがなければ
            # RowNames をキーにする
            else:
                index = self.index(r, 0)  # c は無視される
                key = get_internal_header_data(index, Qt.Orientation.Vertical)

            out.update({key: row_information})

        return out

    def set_data_from_stash(self, item, key, header_data, stashed_data):
        # key は name 列の値 (優先) または internal header
        data: dict[Qt.ItemDataRole, Any] = stashed_data[key][header_data]
        for role, value in data.items():
            item.setData(value, role)

    def _set_dummy_data(self, n_rows=None):
        rows = len(self.ColumnNames)
        columns = len(self.ColumnNames) if n_rows is None else n_rows

        with EditModel(self):
            self.setRowCount(rows + 1)  # header row for treeview

            # table
            for r in range(1, rows + 1):
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
class StandardItemModelWithoutFirstRow(QSortFilterProxyModelOfStandardItemModel):
    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        if not source_parent.isValid():
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
    source_model: QStandardItemModel
    proxy_model: QSortFilterProxyModelOfStandardItemModel

    def __init__(
            self,
            text: str,
            model: QStandardItemModel | QSortFilterProxyModelOfStandardItemModel
    ):
        if isinstance(model, QStandardItemModel):
            self.source_model = model
            self.proxy_model = QSortFilterProxyModelOfStandardItemModel()
            self.proxy_model.setSourceModel(model)
        elif isinstance(model, QSortFilterProxyModelOfStandardItemModel):
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

                proxy_index: QModelIndex = arg

                # prepare new item
                item = QStandardItem()

                # get source item
                source_index = self.proxy_model.mapToSource(proxy_index)
                source_item = self.proxy_model.sourceModel().itemFromIndex(source_index)

                # clone itemData
                data = self.proxy_model.itemData(proxy_index)
                for role, value in data.items():
                    item.setData(value, role)

                # clone other properties
                item.setEditable(source_item.isEditable())
                item.setCheckable(source_item.isCheckable())
                item.setEnabled(source_item.isEnabled())
                item.setSelectable(source_item.isSelectable())
                item.setDragEnabled(source_item.isDragEnabled())
                item.setAutoTristate(source_item.isAutoTristate())
                item.setDropEnabled(source_item.isDropEnabled())
                item.setUserTristate(source_item.isUserTristate())

                # do clone
                r, c = arg.row(), arg.column()
                self.setChild(r, c, item)

    def clone_back(
            self,
            top_left: QModelIndex,  # index of some ItemModel containing ItemModelAsItem
            bottom_right: QModelIndex,
            roles: list[Qt.ItemDataRole],
    ):
        # StandardItemModelAsQStandardItem は
        # 大元の ItemModel が変更されるたび
        # self の Item を更新する仕組みなので
        # この Item を参照する ItemModel を通じて
        # Item が変更された場合その変更は
        # 大元の ItemModel に反映されない。
        # そうしたい場合は、これを使う。
        # ItemModel の dataChanged に connect して
        # self を変更する。

        # まず 順方向 clone を切る
        self.proxy_model.dataChanged.disconnect(self.do_clone)

        # top_left のみ考える
        index = top_left

        # 貰った変更 index を変換する
        proxy_index = self.proxy_model.index(index.row(), index.column())

        # どこかの ItemModel による変更を self から
        # 追って取得する
        data = self.model().data(index)

        with EditModel(self.proxy_model):
            # 変更を適用する
            self.proxy_model.setData(proxy_index, data)

        # 順方向 clone を戻す
        self.proxy_model.dataChanged.connect(self.do_clone)
