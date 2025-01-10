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

from pyfemtet_opt_gui_2.common.qt_util import (
    SortFilterProxyModelOfStandardItemModel,
    StandardItemModelWithHeaderSearch,
    get_enhanced_font,
)

import enum
import logging


__all__ = [
    'CommonItemColumnName',
    'StandardItemModelWithoutFirstRow',
    'StandardItemModelWithEnhancedFirstRow',
    'StandardItemModelAsQStandardItem',
]


# pyfemtet.opt で使う Item の共通部分の列挙体
class CommonItemColumnName(enum.StrEnum):
    use = '使用'


# 各ページで使う、一行目を隠す ProxyModel
class StandardItemModelWithoutFirstRow(SortFilterProxyModelOfStandardItemModel):
    def filterAcceptsRow(self, source_row, source_parent) -> bool:
        if source_row == 0:
            return False
        return True


# 一覧ページで使う、各モデルの一行目を強調する QStandardItemModel
class StandardItemModelWithEnhancedFirstRow(StandardItemModelWithHeaderSearch):

    def data(self, index, role=...):
        if (index.row() == 0) and (role == Qt.ItemDataRole.FontRole):
            return get_enhanced_font()

        return super().data(index, role)


# QStandardItem を StandardItemModel に変換するクラス
# 各 StandardItem を各ページの TableView に表示するために使う
class StandardItemModelAsQStandardItem(QStandardItem):

    original_model: StandardItemModelWithHeaderSearch

    def __init__(self, text: str, model: StandardItemModelWithHeaderSearch):
        assert isinstance(model, StandardItemModelWithHeaderSearch)
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
                item = self.original_model.itemFromIndex(arg).clone()  # ひとつの item はふたつの model に紐づけられない？？
                r, c = arg.row(), arg.column()
                self.setChild(r, c, item)

