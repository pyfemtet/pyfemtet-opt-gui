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

from pyfemtet_opt_gui_2.models.config.algorithm.base import (
    QAbstractAlgorithmItemModel,
    AbstractAlgorithmConfig,
    AbstractAlgorithmConfigItem,
)

import enum


# （アルゴリズムごとの）設定項目
class RandomAlgorithmConfig(AbstractAlgorithmConfig):
    name = 'Random'

    class Items(enum.Enum):
        @enum.member
        class Seed(AbstractAlgorithmConfigItem):
            name = 'seed 値'
            default = 'なし'
            note = ('実行ごとに同じ結果が再現されるようにするには、\n'
                    '自然数を指定してください。ただし Femtet で数値\n'
                    '誤差が入りやすい項目（例：ミーゼス応力）を目的\n'
                    '関数にすると再現しなくなる場合があります。')


# （アルゴリズムごとの）設定値の入力ルール
class RandomAlgorithmDelegate(QStyledItemDelegate):

    def is_seed_value(self, index):
        column_data = get_internal_header_data(index)
        row_data = get_internal_header_data(index, Qt.Orientation.Vertical)

        # `Seed` 行の `value` 列かどうか
        return (
                column_data == QRandomAlgorithmItemModel.ColumnNames.value
                and row_data == RandomAlgorithmConfig.Items.Seed.value.name
        )

    def createEditor(self, parent, option, index):

        if self.is_seed_value(index):
            editor: QLineEdit = QLineEdit(parent=parent)
            return editor

        else:
            return super().createEditor(parent, option, index)

    def setModelData(self, editor, model, index):
        if self.is_seed_value(index):
            editor: QLineEdit
            value = editor.text()
            try:
                value = int(value)
                if value < 0:
                    raise ValueError
                value = str(value)
            except ValueError:
                value = str(RandomAlgorithmConfig.Items.Seed.value.default)
            with EditModel(model):
                model.setData(index, value, Qt.ItemDataRole.DisplayRole)

        else:
            return super().setModelData(editor, model, index)


# （アルゴリズムごとの）設定項目の ItemModel
class QRandomAlgorithmItemModel(QAbstractAlgorithmItemModel):
    AlgorithmConfig: RandomAlgorithmConfig = RandomAlgorithmConfig()

    def get_delegate(self):
        return RandomAlgorithmDelegate()


# シングルトンパターン

_MODEL: QRandomAlgorithmItemModel = None


def get_random_algorithm_config_model(parent) -> QRandomAlgorithmItemModel:
    global _MODEL

    if _MODEL is None:
        _MODEL = QRandomAlgorithmItemModel(parent)

    return _MODEL


if __name__ == '__main__':
    debug_app = QApplication()

    debug_model = QRandomAlgorithmItemModel()

    debug_view = QTreeView()
    debug_view.setModel(debug_model)

    debug_delegate = RandomAlgorithmDelegate()
    debug_view.setItemDelegate(debug_delegate)

    debug_layout = QGridLayout()
    debug_layout.addWidget(debug_view)

    debug_window = QDialog()
    debug_window.setLayout(debug_layout)

    debug_window.show()

    debug_app.exec()
