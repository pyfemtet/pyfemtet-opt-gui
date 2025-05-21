"""
Qt の振る舞いを微調整するユーティリティ
ビジネスルールに関係しない機能のみにする
"""

import os

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

import enum

__all__ = [
    '_is_debugging',
    '_start_debugging',
    '_end_debugging',
    'get_enhanced_font',
    'EditModel',
    'QSortFilterProxyModelOfStandardItemModel',
    'get_internal_header_data',
    'get_column_by_header_data',
    'get_row_by_header_data',
    'StandardItemModelWithHeaderSearch',
    'start_edit_specific_column',
    'QStyledItemDelegateWithCombobox',
    'CustomItemDataRole',
    'ExpandStateKeeper',
    'ResizeColumn',
    'HeaderDataNotFound',
    'UntouchableProgressDialog',
]


# デバッグ用
# ======================================================
DEBUGGING_FLAG_PATH = os.path.join(os.path.dirname(__file__), '.debugging')


def _is_debugging():
    if os.path.isfile(DEBUGGING_FLAG_PATH):
        print('!!!!!!!!!! debug mode !!!!!!!!!!')
        return True
    return False


def _start_debugging():
    if not _is_debugging():
        with open(DEBUGGING_FLAG_PATH, 'w') as f:
            f.write('Now debugging. Remove this file to cancel debugging.')


def _end_debugging():
    if _is_debugging():
        os.remove(DEBUGGING_FLAG_PATH)


# ちょっとしたもの
# ======================================================

# Esc で消せない QProgressDialog
class UntouchableProgressDialog(QProgressDialog):
    def __init__(
            self,
            labelText: str,
            cancelButtonText: str,
            minimum: int,
            maximum: int,
            parent=...,
    ) -> None:
        flags = (Qt.WindowType.CustomizeWindowHint
                 | Qt.WindowType.WindowTitleHint)
        super().__init__(
            labelText,
            cancelButtonText,
            minimum,
            maximum,
            parent,
            flags
        )

        self.setWindowModality(Qt.WindowModality.WindowModal)

        # noinspection PyTypeChecker
        self.setCancelButton(None)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)


# カスタムアイテムロール
class CustomItemDataRole(enum.IntEnum):
    IsExpandedRole = Qt.ItemDataRole.UserRole + 1
    WithFirstRowRole = Qt.ItemDataRole.UserRole + 2
    CustomResizeRole = Qt.ItemDataRole.UserRole + 3


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
        # self.model.beginResetModel()
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        # self.model.endResetModel()
        #
        # # ===== 取りやめた実装 =====
        # # https://doc.qt.io/qt-6/qabstractitemmodel.html#dataChanged
        # # index_1: 変更範囲の開始 index
        # # index_2: 変更範囲の終了 index
        # # roles: list[int]: 変更範囲で変更された itemDataRole のリスト。
        # #     空リストを渡せば全て変更されたとみなす。
        # index_1 = self.model.index(0, 0)
        # index_2 = self.model.index(self.model.rowCount() - 1, self.model.columnCount() - 1)
        # roles = []
        # self.model.dataChanged.emit(index_1, index_2, roles)
        pass


# QSortFilterProxyModel.sourceModel() の入力補完を
# QStandardItemModel に対して行うためのラッパー
class QSortFilterProxyModelOfStandardItemModel(QSortFilterProxyModel):

    def __init__(self, parent):
        super().__init__(parent)
        self.setRecursiveFilteringEnabled(True)

    def sourceModel(self) -> QStandardItemModel:
        s = super().sourceModel()
        assert isinstance(s, QStandardItemModel)
        return s


# Combobox を作成する機能を備えた Delegate
class QStyledItemDelegateWithCombobox(QStyledItemDelegate):

    def __init__(self, parent):
        super().__init__(parent)
        self.combobox_target_header_data: dict[str, tuple[str, str]] = dict()

    def create_combobox(
            self,
            parent: QWidget,
            index: QModelIndex,
            choices: list[str],
            default=None
    ) -> QComboBox:
        # default value の validate
        if default is None:
            default = choices[0]

        # combobox 作成
        cb = QComboBox(parent)
        cb.addItems(choices)
        cb.setCurrentText(default)
        cb.setFrame(False)

        # TODO: 若干不便だがクラッシュしやすいため原因がわかるまで実装とりやめ
        # # combobox の選択を確定したら即時モデルに反映する
        # # (セルの編集状態解除を待たない)
        # def _setModelData(text, editor_: QComboBox, index_):
        #     editor_.setCurrentText(text)
        #     self.setModelData(editor_, index_.model(), index_)
        #
        # cb.currentTextChanged.connect(
        #     lambda text: _setModelData(text, cb, index)
        # )

        # combobox が作成されたら（つまり編集状態になったら）
        # 即時メニューを展開する
        QTimer.singleShot(0, cb.showPopup)

        return cb

    def is_combobox_target(self, index: QModelIndex, key=None):
        header_data = get_internal_header_data(index)
        header_data_v = get_internal_header_data(index, Qt.Orientation.Vertical)

        if key is None:
            # すべてのターゲットにひとつでも該当すれば True
            for value in self.combobox_target_header_data.values():
                if (
                        str(header_data) == str(value[0])
                        and str(header_data_v) == str(value[1])
                ):
                    return True

            # ここまできたら False
            return False

        else:
            # キー指定があればそれと比較
            value = self.combobox_target_header_data[key]
            return (
                    str(header_data) == str(value[0])
                    and str(header_data_v) == str(value[1])
            )

    def sizeHint(self, option, index) -> QSize:
        if self.is_combobox_target(index):
            return self.get_combobox_size_hint(option, index)
        else:
            return super().sizeHint(option, index)

    def get_combobox_size_hint(self, option, index) -> QSize:
        size = super().sizeHint(option, index)
        size.setWidth(20 + size.width())  # combobox の下三角マークの幅
        index.model().setData(index, 20, CustomItemDataRole.CustomResizeRole)
        return size

    def paint(self, painter, option, index) -> None:
        if self.is_combobox_target(index):
            return self.paint_as_combobox(painter, option, index)
        else:
            super().paint(painter, option, index)

    def paint_as_combobox(self, painter, option, index) -> None:
        cb: QtWidgets.QStyleOptionComboBox = QStyleOptionComboBox()
        cb.rect = option.rect
        cb.currentText = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        QtWidgets.QApplication.style().drawComplexControl(QtWidgets.QStyle.ComplexControl.CC_ComboBox, cb, painter)
        QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.ControlElement.CE_ComboBoxLabel, cb, painter)


# 可能なら Expand State を保持する TreeView ユーティリティ
class ExpandStateKeeper:

    def __init__(self, view):
        assert isinstance(view, QTreeView)
        assert view.model() is not None
        self.view = view

        self.save_expand_state()

        view.expanded.connect(self.save_expand_state)
        view.collapsed.connect(self.save_expand_state)
        view.model().dataChanged.connect(self.check_restore_expand_state)
        # view.model().dataChanged.connect(lambda *_: ik.restore_expand_state())

    def _set_data(self, index, value):
        self.view.model().setData(
            index,
            value,
            CustomItemDataRole.IsExpandedRole,
        )

    def save_expand_state(self, index: QModelIndex = None):
        if index is None:
            for r in range(self.view.model().rowCount()):
                for c in range(self.view.model().columnCount()):
                    index = self.view.model().index(r, c)
                    value = self.view.isExpanded(index)
                    self._set_data(index, value)
        else:
            value = self.view.isExpanded(index)
            self._set_data(index, value)

    def _restore_data(self, index: QModelIndex):
        expanded = self.view.model().data(
            index,
            CustomItemDataRole.IsExpandedRole,
        )
        self.view.setExpanded(index, expanded or False)

    def restore_expand_state(self):
        for r in range(self.view.model().rowCount()):
            for c in range(self.view.model().columnCount()):
                index = self.view.model().index(r, c)
                self._restore_data(index)

    def check_restore_expand_state(
            self,
            _1,
            _2,
            roles: list[Qt.ItemDataRole],
    ):
        if CustomItemDataRole.IsExpandedRole in roles:
            # self.save_expand_state()
            pass
        else:
            self.restore_expand_state()


# header の UserDataRole を前提とした QStandardItemModel
# ======================================================

class HeaderDataNotFound(Exception):
    pass


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
        raise HeaderDataNotFound(f'Internal Error! The header data {value} '
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

# dataChanged のスロットとして使える callable クラス
class ResizeColumn:
    _concrete_method: callable = None

    def __init__(self, view: QAbstractItemView):

        if isinstance(view, QTreeView):
            self._concrete_method = self._resize_tree_view
        elif isinstance(view, QTableView):
            self._concrete_method = self._resize_table_view
        else:
            raise NotImplementedError

        self.view = view
        self.view.model().dataChanged.connect(self)

    def __call__(
            self,
            top_left: QModelIndex,
            bottom_right: QModelIndex,
            roles: list[Qt.ItemDataRole],
    ):
        # DisplayRole が変化するときのみ実行
        if (Qt.ItemDataRole.DisplayRole in roles) or len(roles) == 0:
            self._concrete_method(top_left)

    def resize_all_columns(self):
        model = self.view.model()
        for c in range(model.columnCount()):
            for r in range(model.rowCount()):
                index = model.index(r, c)
                self(index, None, [Qt.ItemDataRole.DisplayRole])

    def _set_size_hint(self, index: QModelIndex) -> tuple[QStandardItem, QSize]:

        # item を取得
        model = index.model()
        if isinstance(model, QSortFilterProxyModelOfStandardItemModel):
            model: QSortFilterProxyModelOfStandardItemModel
            source_index = model.mapToSource(index)
            item = model.sourceModel().itemFromIndex(source_index)
        else:
            model: QStandardItemModel
            item = model.itemFromIndex(index)

        # sizeHint を更新
        h = self._calc_required_height(item, self.view)
        w = self._calc_required_width(item, self.view)
        size = QSize(w, h)
        item.setSizeHint(size)

        if item.data(CustomItemDataRole.CustomResizeRole) == 'ignore':
            return item, QSize(1, h)

        return item, size

    def _resize_table_view(self, index: QModelIndex):
        self.view: QTableView

        self._set_size_hint(index)

        self.view.resizeColumnsToContents()
        self.view.resizeRowsToContents()

        # setSectionResizeMode しないと stretchLastSection が無視される
        for logical_index in range(self.view.horizontalHeader().count()):
            self.view.horizontalHeader().setSectionResizeMode(
                logical_index,
                QtWidgets.QHeaderView.ResizeMode.ResizeToContents  # or Interactive
            )

    def _resize_tree_view(self, _index: QModelIndex):
        self.view: QTreeView
        model = self.view.model()

        max_width_list_per_column = dict()

        for c in range(model.columnCount()):
            # この関数を使うと femprj の絶対パスが長いときに
            # 自動的にその長さに合わせてしまう
            # self.view.resizeColumnToContents(c)

            if c not in max_width_list_per_column.keys():
                max_width_list_per_column[c] = 0

            for r in range(model.rowCount()):
                index: QModelIndex = model.index(r, c)
                item, size = self._set_size_hint(index)

                # item の幅で更新
                max_width_list_per_column[c] = max(
                    size.width(), max_width_list_per_column[c]
                )

                # item の children を見る
                if item.hasChildren():

                    for r_ in range(item.rowCount()):
                        for c_ in range(item.columnCount()):
                            # c_ 列がまだなら作る
                            if c_ not in max_width_list_per_column.keys():
                                max_width_list_per_column[c_] = 0

                            child = item.child(r_, c_)
                            if child is not None:
                                child_w = self._calc_required_width(child, self.view)

                                # c_==0 ならインデントぶんの下駄を設定する
                                if c_ == 0:
                                    child_w += 24

                                max_width_list_per_column[c_] = max(
                                    child_w, max_width_list_per_column[c_]
                                )

        for c, width in max_width_list_per_column.items():
            self.view.header().show()
            self.view.header().resizeSections(QHeaderView.ResizeMode.Interactive)
            self.view.header().resizeSection(c, width)

    @staticmethod
    def _calc_required_width(item: QStandardItem, view: QAbstractItemView):

        # magic numbers...
        ICON_SPACE_WIDTH = 24
        CHECKBOX_SPACE_WIDTH = 24
        MARGIN = 8
        other_space = 24

        # 強制的に追加するスペースがあるか
        # (CustomDelegate で Combobox を入れているなど)
        if isinstance(item.data(CustomItemDataRole.CustomResizeRole), int):
            other_space = item.data(CustomItemDataRole.CustomResizeRole)

        # ignore かどうか
        if item.data(CustomItemDataRole.CustomResizeRole) == 'ignore':
            return 0

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

        # get the check-able width
        if item.isCheckable():
            checkbox_width = CHECKBOX_SPACE_WIDTH
        else:
            checkbox_width = 0

        return MARGIN + text_area_width + icon_width + checkbox_width + other_space

    @staticmethod
    def _calc_required_height(item: QStandardItem, view: QAbstractItemView):
        MARGIN = 10

        fm = view.fontMetrics()
        size: QSize = fm.size(Qt.TextFlag.TextShowMnemonic, item.text())
        height = size.height()

        return height + MARGIN
