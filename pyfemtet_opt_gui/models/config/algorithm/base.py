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
from pyfemtet_opt_gui.common.qt_util import *
# noinspection PyUnresolvedReferences
from pyfemtet_opt_gui.common.pyfemtet_model_bases import *
# noinspection PyUnresolvedReferences
from pyfemtet_opt_gui.common.return_msg import *
# noinspection PyUnresolvedReferences
from pyfemtet_opt_gui.common.expression_processor import *

import enum
from abc import ABC


# これを使うと ConfigModel と ConfigModelForProblem の同期がかなり複雑になるので実装とりやめ
# # （共通の）ProblemView に表示するための ModelAsItem に使用するための Model
# class QAlgorithmItemModelForProblem(QSortFilterProxyModelOfStandardItemModel):
#
#     def filterAcceptsColumn(self, source_column: int, source_parent: QModelIndex):
#         # note を非表示
#         source_model: QAbstractAlgorithmItemModel = self.sourceModel()
#         if source_column == get_column_by_header_data(
#                 source_model,
#                 QAbstractAlgorithmItemModel.ColumnNames.note
#         ):
#             return False
#
#         return super().filterAcceptsColumn(source_column, source_parent)


# （共通の）Treeview に表示するための Algorithm の ItemModelAsItem
class QAlgorithmStandardItem(StandardItemModelAsQStandardItem):

    def __init__(self, text: str, model: StandardItemModelWithHeaderSearch | QSortFilterProxyModelOfStandardItemModel):
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
    note = '設定項目の説明'


# （アルゴリズムごとの）設定全体
class AbstractAlgorithmConfig:
    name = 'Abstract Algorithm'
    note = 'GUI のデバッグ用の項目です。'

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

    def __init__(self, parent=None):
        StandardItemModelWithHeaderSearch.__init__(self, parent)
        self.setup_header_data()
        self.setup_vertical_header_data()
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

    # abstract
    def output_json(self):
        out = dict(
            ret='opt',
            command='OptunaOptimizer',
            args=dict(
                sampler_class='TPESampler',
                sampler_kwargs=dict(
                    n_startup_trials=10,
                )
            )
        )

        import json
        return json.dumps([out])


# シングルトンパターン

_MODEL: QAbstractAlgorithmItemModel | None = None


def get_abstract_algorithm_config_model(parent) -> QAbstractAlgorithmItemModel:
    global _MODEL

    if _MODEL is None:
        _MODEL = QAbstractAlgorithmItemModel(parent)

    return _MODEL


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
