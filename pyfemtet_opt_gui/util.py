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

from pyfemtet_opt_gui.item_as_model import MyStandardItemAsTableModelWithoutHeader, MyStandardItemAsTableModel


def start_edit_specific_column(edit_fun, col_data, *args):
    # 前提
    # view: MyStandardItemAsTableModelWithoutHeader を model とする view
    # MyStandardItemAsTableModelWithoutHeader: sourceModel を持つ ProxyModel


    for arg in args:
        print(arg)
        if isinstance(arg, QModelIndex):
            proxy_index: QModelIndex = arg
            proxy_model: QSortFilterProxyModel = proxy_index.model()
            source_model: QStandardItemModel = proxy_model.sourceModel()
            source_index: QModelIndex = proxy_model.mapToSource(proxy_index)
            r = 0
            c = source_index.column()
            target_index = source_model.index(r, c)
            header_text = source_model.data(target_index, Qt.ItemDataRole.EditRole)
            if header_text == col_data:
                edit_fun(proxy_index)

    print()
