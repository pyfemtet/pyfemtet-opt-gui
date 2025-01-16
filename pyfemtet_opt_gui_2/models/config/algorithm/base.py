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

# noinspection PyUnresolvedReferences
from contextlib import nullcontext

# noinspection PyUnresolvedReferences
from pyfemtet_opt_gui_2.common.qt_util import *
# noinspection PyUnresolvedReferences
from pyfemtet_opt_gui_2.common.pyfemtet_model_bases import *
# noinspection PyUnresolvedReferences
from pyfemtet_opt_gui_2.common.return_msg import *
# noinspection PyUnresolvedReferences
from pyfemtet_opt_gui_2.common.expression_processor import *
# noinspection PyUnresolvedReferences
from pyfemtet_opt_gui_2.femtet.femtet import *

import enum
from abc import ABC


# （共通の）Treeview に表示するための Algorithm の ItemModelAsItem
class QAlgorithmStandardItem(StandardItemModelAsQStandardItem):

    def __init__(self, text: str, model: StandardItemModelWithHeaderSearch | SortFilterProxyModelOfStandardItemModel):
        super().__init__(text, model)
        self.setEditable(False)
        self.name = text


# （共通の）アルゴリズムの設定の HeaderData
class AlgorithmItemModelColumnNames(enum.StrEnum):
    name = '項目'
    value = '値'
    note = '備考'


# ===== ここから下のクラスを継承する =====

# （アルゴリズムごとの）設定項目のベース
class AbstractAlgorithmConfigItem(ABC):
    name = '何かの設定項目'
    default = '何かのデフォルト値'
    note = '設定項目の備考'


# （アルゴリズムごとの）設定全体
class AbstractAlgorithmConfig:
    name = 'Abstract Algorithm'

    class Items(enum.Enum):
        # abstract class
        @enum.member
        class FloatItem(AbstractAlgorithmConfigItem):
            name = '数値の設定項目'
            default = 0.
            ub = None
            lb = None

        # abstract class
        @enum.member
        class StrItem(AbstractAlgorithmConfigItem):
            name = '文字列の設定項目'
            default = '既定の値'
            choices = [
                default,
                '選択肢2',
                '選択肢3'
            ]


# （アルゴリズムごとの）設定項目の ItemModel
class QAbstractAlgorithmItemModel(StandardItemModelWithHeader):
    with_first_row = False
    ColumnNames = AlgorithmItemModelColumnNames

    # abstract
    AlgorithmConfig: AbstractAlgorithmConfig = AbstractAlgorithmConfig()

    def __init__(self, parent=None, _with_dummy=True):
        StandardItemModelWithHeaderSearch.__init__(self, parent)
        self.setup_header_data(self.ColumnNames)
        self.setup_model()

    @property
    def name(self):
        return self.AlgorithmConfig.name

    @property
    def RowNames(self):
        return [item.value.name for item in self.AlgorithmConfig.Items]

    def setup_model(self):
        rows = len(self.AlgorithmConfig.Items)
        columns = len(self.ColumnNames)

        with EditModel(self):
            self.setRowCount(rows)
            self.setColumnCount(columns)

            item_cls: AbstractAlgorithmConfigItem
            for r, item_cls in enumerate([enum_item.value for enum_item in self.AlgorithmConfig.Items]):

                name = item_cls.name
                value = item_cls.default
                note = item_cls.note

                # name
                with nullcontext():
                    c = self.get_column_by_header_data(self.ColumnNames.name)
                    item: QStandardItem = QStandardItem()
                    item.setEditable(False)
                    item.setText(name)
                    self.setItem(r, c, item)

                # value
                with nullcontext():
                    c = self.get_column_by_header_data(self.ColumnNames.value)
                    item: QStandardItem = QStandardItem()
                    item.setText(str(value))
                    self.setItem(r, c, item)

                # note
                with nullcontext():
                    c = self.get_column_by_header_data(self.ColumnNames.note)
                    item: QStandardItem = QStandardItem()
                    item.setEditable(False)
                    item.setText(str(note))
                    self.setItem(r, c, item)

    # abstract
    def get_delegate(self):
        return QStyledItemDelegate()


# シングルトンパターン

_MODEL: QAbstractAlgorithmItemModel = None
_ITEM: QAlgorithmStandardItem = None


def get_abstract_algorithm_config_item(parent) -> QAlgorithmStandardItem:
    global _MODEL, _ITEM

    if _MODEL is None:
        _MODEL = QAbstractAlgorithmItemModel(parent)

    if _ITEM is None:
        _ITEM = QAlgorithmStandardItem(AbstractAlgorithmConfig.name, _MODEL)

    return _ITEM


if __name__ == '__main__':
    debug_app = QApplication()

    debug_model = QAbstractAlgorithmItemModel()

    debug_view = QTreeView()
    debug_view.setModel(debug_model)

    debug_layout = QGridLayout()
    debug_layout.addWidget(debug_view)

    debug_window = QDialog()
    debug_window.setLayout(debug_layout)

    debug_window.show()

    debug_app.exec()
