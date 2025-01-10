"""
Qt の振る舞いを微調整するユーティリティ
ビジネスルールに関係しない機能のみにする
"""

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


__all__ = [
    'get_enhanced_font',
    'EditModel',
    'SortFilterProxyModelOfStandardItemModel',
    'get_internal_header_data',
    'get_column_by_header_data',
    'StandardItemModelWithHeaderSearch',
    'start_edit_specific_column',
    'resize_column',
]


# ちょっとしたもの
# ======================================================

# bold font の規定値
def get_enhanced_font():
    font = QFont()
    font.setBold(True)
    font.setItalic(True)
    return font


# モデル編集を Start, End するためのコンテキストマネージャ
class EditModel:

    model: QAbstractItemModel

    def __init__(self, model: QAbstractItemModel):
        self.model = model

    def __enter__(self):
        self.model.beginResetModel()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.model.endResetModel()


# QSortFilterProxyModel の入力補完を QStandardItemModel に
# 対して行うためのラッパー
class SortFilterProxyModelOfStandardItemModel(QSortFilterProxyModel):
    def sourceModel(self) -> QStandardItemModel:
        s = super().sourceModel()
        assert isinstance(s, QStandardItemModel)
        return s


# header の UserDataRole を前提とした QStandardItemModel
# ======================================================

# index の位置に対応する UserRole の headerData を取得
def get_internal_header_data(index, orientation=Qt.Orientation.Horizontal):
    if orientation == Qt.Orientation.Horizontal:
        return index.model().headerData(
            _section := index.column(),
            _orientation := Qt.Orientation.Horizontal,
            _role := Qt.ItemDataRole.UserRole,
        )
    else:
        return index.model().headerData(
            _section := index.row(),
            _orientation := Qt.Orientation.Vertical,
            _role := Qt.ItemDataRole.UserRole,
        )


# value に対応する column 又は index を取得
def get_column_by_header_data(model: QStandardItemModel, value, r=None) -> int | QModelIndex:
    # return index or int
    if r is None:
        r = 0  # dummy
        return_index = False
    else:
        return_index = True

    # search the value
    for c in range(model.columnCount()):
        index = model.index(r, c)
        if get_internal_header_data(index) == value:
            if return_index:
                return index
            else:
                return c

    # not found
    else:
        raise RuntimeError(f'Internal Error! The header data {value} '
                           f'is not found.')


# header ユーティリティを有する関数
class StandardItemModelWithHeaderSearch(QStandardItemModel):

    def get_column_by_header_data(self, value, r=None) -> int | QModelIndex:
        return get_column_by_header_data(self, value, r)


# QTableView の振る舞いの微調整
# ======================================================

# 特定の internal header data だけに適用できるスロットとして使える
# コントロールの編集開始関数
def start_edit_specific_column(edit_fun, header_value, *args, **_kwargs):
    """
    特定の internal header data だけに適用できるスロットとして使える
    コントロールの編集開始関数


    Usage:
        >>> control = ...
        >>> control.clicked.connect(
        ...     lambda *a, **kw:
        ...         start_edit_specific_column(
        ...             control.edit,
        ...             'direction',  # internal header data
        ...             *a, **kw
        ...         )
        ... )
        ...
    """

    for arg in args:
        if isinstance(arg, QModelIndex):
            index: QModelIndex = arg
            if get_internal_header_data(index) == header_value:
                edit_fun(index)
                break


# QTableView の要素が変更されるたび列幅を調整する機能群
# ------------------------------------------------------

# スロットとして使える callable クラス
class _ResizeColumn(object):
    def __call__(self, view: QTreeView | QTableView, *args):
        for arg in args:

            # item
            if isinstance(arg, QStandardItem):
                item: QStandardItem = arg

                h = self.calc_required_height(item, view)
                w = self.calc_required_width(item, view)
                size = QSize(w, h)
                item.setSizeHint(size)

                if isinstance(view, QTreeView):
                    view.resizeColumnToContents(item.index().column())

            # modelindex
            elif isinstance(arg, QModelIndex):
                index: QModelIndex = arg

                model = index.model()

                if isinstance(model, SortFilterProxyModelOfStandardItemModel):
                    model: SortFilterProxyModelOfStandardItemModel
                    source_index = model.mapToSource(index)
                    item = model.sourceModel().itemFromIndex(source_index)

                else:
                    model: QStandardItemModel
                    item = model.itemFromIndex(index)

                h = self.calc_required_height(item, view)
                w = self.calc_required_width(item, view)
                size = QSize(w, h)
                item.setSizeHint(size)

                if isinstance(view, QTreeView):
                    view.resizeColumnToContents(item.index().column())

        if isinstance(view, QTableView):
            view.resizeColumnsToContents()
            view.resizeRowsToContents()

            # setSectionResizeMode しないと stretchLastSection が無視される
            for logical_index in range(view.horizontalHeader().count()):
                view.horizontalHeader().setSectionResizeMode(
                    logical_index,
                    QtWidgets.QHeaderView.ResizeMode.ResizeToContents  # or Interactive
                )

    @staticmethod
    def calc_required_width(item: QStandardItem, view: QAbstractItemView):
        # magic numbers...
        ICON_SPACE_WIDTH = 24
        CHECKBOX_SPACE_WIDTH = 24
        MARGIN = 8

        # fontMetrics to calc the required width of text
        fm = view.fontMetrics()

        # get the width of required text region
        text_area_width = fm.size(Qt.TextFlag.TextShowMnemonic, item.text()).width()

        # get the width of icon
        if item.icon().isNull():
            icon_width = 0
        else:
            # ----- The following code snippets doesn't work as intended... -----
            # width: int = view.horizontalHeader().sectionSize(item.column())
            # height: int = view.verticalHeader().sectionSize(item.row())
            # required_size = QSize(width, height)
            # icon_size = item.icon().actualSize(required_size)
            # icon_width = icon_size.width()
            # logger.debug(f'{icon_width=}')
            icon_width = ICON_SPACE_WIDTH

        # get the checkable width
        if item.isCheckable():
            checkbox_width = CHECKBOX_SPACE_WIDTH
        else:
            checkbox_width = 0

        return MARGIN + text_area_width + icon_width + checkbox_width

    @staticmethod
    def calc_required_height(item: QStandardItem, view: QAbstractItemView):
        MARGIN = 10

        fm = view.fontMetrics()
        size: QSize = fm.size(Qt.TextFlag.TextShowMnemonic, item.text())
        height = size.height()

        return height + MARGIN


# スロットとして使える callable オブジェクト
resize_column = _ResizeColumn()
