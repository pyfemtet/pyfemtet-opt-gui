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

from pyfemtet_opt_gui.models.config.algorithm.base import (
    QAbstractAlgorithmItemModel,
    AbstractAlgorithmConfig,
)

import enum


# （アルゴリズムごとの）設定項目
class RandomAlgorithmConfig(AbstractAlgorithmConfig):
    name = 'Random'
    note = 'Optuna 実装に基づくランダムサンプリング'

    class Items(enum.Enum):
        pass


# （アルゴリズムごとの）設定値の入力ルール
class RandomAlgorithmDelegate(QStyledItemDelegate):
    pass


# （アルゴリズムごとの）設定項目の ItemModel
class QRandomAlgorithmItemModel(QAbstractAlgorithmItemModel):
    AlgorithmConfig: RandomAlgorithmConfig = RandomAlgorithmConfig()

    def get_delegate(self):
        return RandomAlgorithmDelegate()

    def output_json(self):
        """
        opt = OptunaOptimizer(
            sampler_class=RandomSampler,
        )
        """
        out = dict(
            ret='opt',
            command='OptunaOptimizer',
            args=dict(
                sampler_class='RandomSampler',
            )
        )
        import json
        return json.dumps([out])


# シングルトンパターン

_MODEL: QRandomAlgorithmItemModel | None = None


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
