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
import logging


__all__ = [
    'CommonItemColumnName',
    'EditModel',
    'SortFilterProxyModelOfStandardItemModel',
    'horizontal_header_data_is',
    'vertical_header_data_is',
    'StyledItemDelegateWithHeaderSearch',
    'start_edit_specific_column',
    'resize_column',
    'StandardItemModelWithoutHeader',
    'StandardItemModelAsQStandardItem',
    'StandardItemModelWithHeaderSearch',
]



class CommonItemColumnName(enum.StrEnum):
    use = 'use'
    name = 'name'


class EditModel:

    model: QAbstractItemModel

    def __init__(self, model: QAbstractItemModel):
        self.model = model

    def __enter__(self):
        self.model.beginResetModel()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.model.endResetModel()


class SortFilterProxyModelOfStandardItemModel(QSortFilterProxyModel):
    def sourceModel(self) -> QStandardItemModel:
        return super().sourceModel()


def get_internal_horizontal_header_data(index):
    return index.model().headerData(
        _section := index.column(),
        _orientation := Qt.Orientation.Horizontal,
        _role := Qt.ItemDataRole.UserRole,
    )


def get_internal_vertical_header_data(index):
    return index.model().headerData(
        _section := index.row(),
        _orientation := Qt.Orientation.Vertical,
        _role := Qt.ItemDataRole.UserRole,
    )


def horizontal_header_data_is(index, value) -> bool:
    return get_internal_horizontal_header_data(index) == value


def vertical_header_data_is(index, value) -> bool:
    return get_internal_vertical_header_data(index) == value


class StyledItemDelegateWithHeaderSearch(QStyledItemDelegate):
    def get_internal_horizontal_header_data(self, index):
        return get_internal_horizontal_header_data(index)

    def get_internal_vertical_header_data(self, index):
        return get_internal_vertical_header_data(index)

    def horizontal_header_data_is(self, index, value) -> bool:
        return get_internal_horizontal_header_data(index) == value

    def vertical_header_data_is(self, index, value) -> bool:
        return get_internal_vertical_header_data(index) == value


class StandardItemModelWithHeaderSearch(QStandardItemModel):
    def get_column_by_header_data(self, value, r=None):

        return_index = True
        if r is None:
            r = 0
            return_index = False

        for c in range(self.columnCount()):
            index = self.index(r, c)
            if horizontal_header_data_is(index, value):
                if return_index:
                    return index
                else:
                    return c
        else:
            print(c)
            raise RuntimeError('Internal Error!')

    def data(self, index, role=...):

        if (index.row() == 0) and (role == Qt.ItemDataRole.FontRole):
            font = QFont()
            font.setBold(True)
            font.setItalic(True)
            return font

        return super().data(index, role)


def start_edit_specific_column(edit_fun, col_data, *args, **_kwargs):
    # ===== debug logger settings =====
    logger = logging.getLogger('GUI.filter_index')
    logger.setLevel(logging.WARN)
    logger.debug(f'===== {logger.name.split('.')[-1]}() start =====')
    # =================================

    logger.debug(args)
    # -> (<PySide6.QtCore.QModelIndex(0,2,0x14a702130d0,ObjectiveProxyModel(0x14a72ddb200)) at 0x0000014A71F7F4C0>,)

    for arg in args:
        if isinstance(arg, QModelIndex):
            index: QModelIndex = arg
            value = index.model().headerData(
                index.column(),
                Qt.Orientation.Horizontal,
                Qt.ItemDataRole.UserRole
            )
            if value == col_data:
                edit_fun(index)


def resize_column(view: QTreeView | QTableView, *args, **_kwargs):
    # ===== debug logger settings =====
    logger = logging.getLogger('GUI.resize_column')
    logger.setLevel(logging.WARN)
    logger.debug(f'===== {logger.name.split('.')[-1]}() start =====')
    # =================================

    logger.debug(args)
    # (<PySide6.QtGui.QStandardItem object at 0x000001D9E669A940>,),
    # (<PySide6.QtCore.QModelIndex(0,1,0x1d9e4b347e0,ObjectiveTableItemModel(0x1d9e4b0dbc0)) at 0x000001D9E669B440>, <PySide6.QtCore.QModelIndex(0,1,0x1d9e4b347e0,ObjectiveTableItemModel(0x1d9e4b0dbc0)) at 0x000001D9E669B500>, [0, 2])

    # contains items or indices (assuming start and end of rect?)
    for arg in args:

        # item
        if isinstance(arg, QStandardItem):
            item: QStandardItem = arg
            h = calc_required_height(item, view)
            w = calc_required_width(item, view)
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

            h = calc_required_height(item, view)
            w = calc_required_width(item, view)
            size = QSize(w, h)
            item.setSizeHint(size)

            if isinstance(view, QTreeView):
                view.resizeColumnToContents(item.index().column())

    if isinstance(view, QTableView):
        view.resizeColumnsToContents()
        view.resizeRowsToContents()


def calc_required_width(item: QStandardItem, view: QAbstractItemView):
    # ===== debug logger settings =====
    logger = logging.getLogger('GUI.calc_required_width')
    logger.setLevel(logging.WARN)
    logger.debug(f'===== {logger.name.split('.')[-1]}() start =====')
    # =================================

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


def calc_required_height(item: QStandardItem, view: QAbstractItemView):
    # ===== debug logger settings =====
    logger = logging.getLogger('GUI.calc_required_height')
    logger.setLevel(logging.WARN)
    logger.debug(f'===== {logger.name.split('.')[-1]}() start =====')
    # =================================

    MARGIN = 8

    fm = view.fontMetrics()
    size: QSize = fm.size(Qt.TextFlag.TextShowMnemonic, item.text())
    height = size.height()

    return height + MARGIN


class StandardItemModelWithoutHeader(SortFilterProxyModelOfStandardItemModel):
    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        if source_row == 0:
            return False
        return True


class StandardItemModelAsQStandardItem(QStandardItem):

    original_model: QStandardItemModel

    def __init__(self, text: str, model: QStandardItemModel):
        self.original_model = model
        super().__init__(self.original_model.rowCount(), self.original_model.columnCount())
        self.setText(text)
        self.do_clone_all()
        self.original_model.dataChanged.connect(self.do_clone)

    def do_clone_all(self):
        indices = []
        for r in range(self.original_model.rowCount()):
            for c in range(self.original_model.columnCount()):
                indices.append(self.original_model.index(r, c))
        self.do_clone(*indices)

    def do_clone(self, *args, **kwargs):
        # ===== debug logger settings =====
        logger = logging.getLogger('GUI.do_clone')
        logger.setLevel(logging.WARN)
        logger.debug(f'===== {logger.name.split('.')[-1]}() start =====')
        # =================================

        for arg in args:
            if isinstance(arg, QModelIndex):
                item = self.original_model.itemFromIndex(arg).clone()  # ひとつの item はふたつの　model に紐づけられない？？
                r, c = arg.row(), arg.column()
                self.setChild(r, c, item)
