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
    'DelegateWithCombobox',
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

    def __init__(self, model: QAbstractItemModel, index: QModelIndex = None, roles: list[Qt.ItemDataRole] = None):
        self.model = model
        self.index = index
        self.roles = roles if roles is not None else []

    def __enter__(self):
        # beginResetModel-endResetModel を使うと
        # その間別の処理が model にアクセスすると
        # アプリケーションがクラッシュするらしい
        # ので dataChanged を emit する方式に変更
        # self.model.beginResetModel()
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.model.endResetModel()

        if self.index is None:
            index_1 = self.model.index(0, 0)
            index_2 = self.model.index(self.model.rowCount() - 1, self.model.columnCount() - 1)
        else:
            index_1 = index_2 = self.index

        # https://doc.qt.io/qt-6/qabstractitemmodel.html#dataChanged
        # index_1: 変更範囲の開始 index
        # index_2: 変更範囲の終了 index
        # roles: list[int]: 変更範囲で変更された itemDataRole のリスト。
        #     空リストを渡せば全て変更されたとみなす。
        self.model.dataChanged.emit(index_1, index_2, self.roles)


# QSortFilterProxyModel の入力補完を QStandardItemModel に
# 対して行うためのラッパー
class SortFilterProxyModelOfStandardItemModel(QSortFilterProxyModel):
    def sourceModel(self) -> QStandardItemModel:
        s = super().sourceModel()
        assert isinstance(s, QStandardItemModel)
        return s


# Combobox を作成する機能を備えた Delegate
class DelegateWithCombobox(QStyledItemDelegate):

    target_indices: set[QModelIndex]

    def __init__(self, parent):
        super().__init__(parent)
        self.target_indices = set()

    def update_model(self, index, text):
        model = index.model()
        with EditModel(model):
            model.setData(index, text, Qt.ItemDataRole.DisplayRole)

    def create_combobox(
            self,
            parent: QWidget,
            index: QModelIndex,
            choices: list[str],
            default=None
    ) -> QWidget:

        # 本来の setModelData を prevent するために
        self.target_indices.add(index)

        # default value の validate
        if default is None:
            default = choices[0]

        # combobox 作成
        cb = QComboBox(parent)
        cb.addItems(choices)
        cb.setCurrentText(default)
        cb.setFrame(False)

        # combobox の選択を変更したらセルの値も変更して
        # combobox のあるセルに基づいて振る舞いが変わる
        # セルのふるまいを即時変えるようにする
        cb.currentTextChanged.connect(
            lambda text: self.update_model(index, text)
        )

        # combobox が作成されたら（つまり編集状態になったら）
        # 即時メニューを展開する
        QTimer.singleShot(0, cb.showPopup)

        return cb

    def setEditorData(self, editor, index):
        if index in self.target_indices:
            return
        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if index in self.target_indices:
            return
        else:
            super().setModelData(editor, model, index)

    def get_combobox_size_hint(self, option, index) -> QSize:
        size = super().sizeHint(option, index)
        size.setWidth(24 + size.width())  # combobox の下三角マークの幅
        return size

    def paint_as_combobox(self, painter, option, index):
        cb: QtWidgets.QStyleOptionComboBox = QStyleOptionComboBox()
        cb.rect = option.rect
        cb.currentText = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        QtWidgets.QApplication.style().drawComplexControl(QtWidgets.QStyle.ComplexControl.CC_ComboBox, cb, painter)
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.ControlElement.CE_ComboBoxLabel, cb, painter)


# header の UserDataRole を前提とした QStandardItemModel
# ======================================================

# index の位置に対応する UserRole の headerData を取得
def get_internal_header_data(index: QModelIndex, orientation=Qt.Orientation.Horizontal):
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


def get_row_by_header_data(model: QStandardItemModel, value, c=None) -> int | QModelIndex:
    # return index or int
    if c is None:
        c = 0  # dummy
        return_index = False
    else:
        return_index = True

    # search the value
    for r in range(model.rowCount()):
        index = model.index(r, c)
        if get_internal_header_data(index, orientation=Qt.Orientation.Vertical) == value:
            if return_index:
                return index
            else:
                return r

    # not found
    else:
        raise RuntimeError(f'Internal Error! The header data {value} '
                           f'is not found.')


# header ユーティリティを有する関数
class StandardItemModelWithHeaderSearch(QStandardItemModel):

    def get_column_by_header_data(self, value, r=None) -> int | QModelIndex:
        return get_column_by_header_data(self, value, r)

    def get_row_by_header_data(self, value, c=None) -> int | QModelIndex:
        return get_row_by_header_data(self, value, c)


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
