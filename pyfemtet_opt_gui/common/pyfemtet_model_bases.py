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

from pyfemtet_opt_gui.common.qt_util import *

import enum
from typing import Any

__all__ = [
    'CommonItemColumnName',
    'StandardItemModelWithoutFirstRow',
    'StandardItemModelWithEnhancedFirstRow',
    'StandardItemModelAsQStandardItem',
    'StandardItemModelWithHeader',
    'ProxyModelWithForProblem',
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

    column_name_display_map = dict()

    def __init__(
            self,
            parent=None,
            _dummy_data=None,
            with_first_row=True
    ):
        super().__init__(parent)

        self.with_first_row = with_first_row
        self.setup_header_data()
        self.setup_vertical_header_data()

        if _dummy_data:
            self._set_dummy_data(_dummy_data)

    def setup_header_data(self):

        HeaderNames = self.ColumnNames

        with EditModel(self):

            self.setColumnCount(len(HeaderNames))
            for c, name in enumerate(HeaderNames):

                display_name = self.column_name_display_map[name] if name in self.column_name_display_map else name

                # displayData
                self.setHeaderData(
                    _section := c,
                    _orientation := Qt.Orientation.Horizontal,
                    _value := display_name,
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
                    display_name = self.column_name_display_map[name] if name in self.column_name_display_map else name
                    item = QStandardItem()
                    item.setText(display_name)
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

                # self.setHeaderData(
                #     _section := r,
                #     _orientation := Qt.Orientation.Vertical,
                #     _value := name,
                #     _role := Qt.ItemDataRole.DisplayRole,
                # )

    def stash_current_table(self) -> dict[str, dict[str, dict[Qt.ItemDataRole, Any]]]:
        """load 時に既存のデータを上書きする為に stash する

        dict[name, dict[ColumnName, dict[Qt.ItemDataRole, Any]]

        """

        out = dict()

        # 既存データについて iteration
        for r in range(1, self.rowCount()):

            # 行ごとに dict を作成, key は obj_name など headerData
            row_information: dict[Any, dict[Qt.ItemDataRole, ...]] = dict()

            # 列ごとにデータを収取
            for header_name in self.ColumnNames:
                c = self.get_column_by_header_data(header_name)
                index = self.index(r, c)
                data: dict[int, Any] = self.itemData(index)
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

    def _set_dummy_data(self, _dummy_data: dict):
        n_rows = 3
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

    def get_row_iterable(self):
        if self.with_first_row:
            return range(1, self.rowCount())
        else:
            return range(self.rowCount())


# 各ページで使う、一行目を隠す ProxyModel
class StandardItemModelWithoutFirstRow(QSortFilterProxyModelOfStandardItemModel):
    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        if not source_parent.isValid():
            if source_row == 0:
                return False
        return True


# 各サブモデルが一覧ページで隠す・表示する ProxyModel
class ProxyModelWithForProblem(QSortFilterProxyModelOfStandardItemModel):
    
    def filterAcceptsColumn(self, source_column, source_parent):

        source_model: StandardItemModelWithHeader = self.sourceModel()
        assert isinstance(source_model, StandardItemModelWithHeader)
        
        # use 列を隠す
        if source_column == source_model.get_column_by_header_data(CommonItemColumnName.use):
            return False
        
        return super().filterAcceptsColumn(source_column, source_parent)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):

        source_model: StandardItemModelWithHeader = self.sourceModel()
        assert isinstance(source_model, StandardItemModelWithHeader)

        # with_first_row なら 1 行目は表示する
        if (
                source_model.with_first_row
                and source_row == 0
        ):
            return True

        # use が unchecked なら隠す
        index = source_model.get_column_by_header_data(CommonItemColumnName.use, source_row)
        item = source_model.itemFromIndex(index)
        if item.checkState() == Qt.CheckState.Unchecked:
            return False

        return super().filterAcceptsRow(source_row, source_parent)


# 一覧ページで使う、各モデルの一行目を強調する QStandardItemModel
class StandardItemModelWithEnhancedFirstRow(StandardItemModelWithHeaderSearch):

    def should_enhance(self, index: QModelIndex) -> bool:
        if not index.isValid():
            return False

        # CustomItemDataRole.WithFirstRowRole stores
        # StandardItemModelWithHeader's withFirstRow
        # or nothing. (if True it / if False or None do nothing)

        # 親がなければ強調の必要なし
        if not index.parent().isValid():
            return False

        # WithFirstRowRole が True でなければ
        # (False か None の可能性がある)
        # 強調の必要なし
        if not index.data(CustomItemDataRole.WithFirstRowRole):
            return False

        # 1 行目でなければ強調の必要なし
        if index.row() != 0:
            return False

        return True

    def data(self, index, role=...):

        if role == Qt.ItemDataRole.FontRole:
            if self.should_enhance(index):
                return get_enhanced_font()

        if role == Qt.ItemDataRole.BackgroundRole:
            if self.should_enhance(index):
                default_color = QApplication.palette().color(QPalette.ColorRole.Base)
                return default_color.darker(120)

        return super().data(index, role)


# QStandardItem を StandardItemModel に変換するクラス
# 各 StandardItem を各ページの TableView に表示するために使う
class StandardItemModelAsQStandardItem(QStandardItem):
    source_model: QStandardItemModel
    proxy_model: QSortFilterProxyModelOfStandardItemModel
    _original_model_is_proxy: bool

    def __init__(
            self,
            text: str,
            model: QStandardItemModel | QSortFilterProxyModelOfStandardItemModel
    ):
        if isinstance(model, QStandardItemModel):
            self._original_model_is_proxy = False
            self._source_model = model
            self.proxy_model = QSortFilterProxyModelOfStandardItemModel(model.parent())
            self.proxy_model.setSourceModel(model)

        elif isinstance(model, QSortFilterProxyModelOfStandardItemModel):
            self._original_model_is_proxy = True
            self.proxy_model = model

        else:
            raise NotImplementedError

        super().__init__(self.proxy_model.rowCount(), self.proxy_model.columnCount())
        self.setText(text)
        self.do_clone_all()
        self.proxy_model.dataChanged.connect(self.do_clone)
        self.proxy_model.rowsMoved.connect(lambda *_: self.do_clone_all())
        self.proxy_model.rowsRemoved.connect(lambda *_: self.do_clone_all())
        self.proxy_model.rowsInserted.connect(lambda *_: self.do_clone_all())
        self.proxy_model.columnsMoved.connect(lambda *_: self.do_clone_all())
        self.proxy_model.columnsRemoved.connect(lambda *_: self.do_clone_all())
        self.proxy_model.columnsInserted.connect(lambda *_: self.do_clone_all())

    @property
    def source_model(self) -> QStandardItemModel | StandardItemModelWithHeader:
        if self._original_model_is_proxy:
            return self.proxy_model.sourceModel()

        else:
            return self._source_model

    def do_clone_all(self):
        self.setRowCount(self.proxy_model.rowCount())
        self.setColumnCount(self.proxy_model.columnCount())
        for r in range(self.proxy_model.rowCount()):
            for c in range(self.proxy_model.columnCount()):
                self.do_clone(self.proxy_model.index(r, c), self.proxy_model.index(r, c), [])

    def do_clone(self, top_left, _bottom_right, _roles):

        # 与えられているのは self.proxy_model の index
        proxy_index: QModelIndex = top_left

        # 自身の直接の子の変更のみ考慮する。
        # 孫以降はその ItemAsModel の do_clone で
        # 処理させるため。
        # Note:
        #   純 QStandardItem に setChild している場合は
        #   無視されてしまうので、そういうデータを実装
        #   する場合はその時に考える。
        if proxy_index.parent().isValid():
            return

        # get source item
        source_index = self.proxy_model.mapToSource(proxy_index)
        source_item = self.proxy_model.sourceModel().itemFromIndex(source_index)

        # clone item
        item = source_item.clone()

        # if clone source model is a
        # StandardItemModelWithHeader,
        # check `with_first_row` attribute
        # and set the value to the item's
        # CustomDataRole.
        with_first_row = False
        if isinstance(self.source_model, StandardItemModelWithHeader):
            with_first_row = self.source_model.with_first_row
        item.setData(with_first_row, CustomItemDataRole.WithFirstRowRole)

        # 直接の子アイテムを clone する
        # 多分、dataChange の連鎖で勝手に再帰する
        if source_item.hasChildren():
            rows = source_item.rowCount()
            columns = source_item.columnCount()
            for r in range(rows):
                for c in range(columns):
                    child = source_item.child(r, c)
                    if child is not None:
                        item.setChild(r, c, child.clone())

        # do clone
        r, c = proxy_index.row(), proxy_index.column()
        self.setChild(r, c, item)
