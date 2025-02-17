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
    AbstractAlgorithmConfigItem,
)

import enum


# （アルゴリズムごとの）設定項目
class NSGAIIAlgorithmConfig(AbstractAlgorithmConfig):
    name = 'NSGA2'
    note = 'Optuna 実装に基づく遺伝的アルゴリズム'

    class Items(enum.Enum):
        @enum.member
        class population_size(AbstractAlgorithmConfigItem):
            name = '1 世代あたりの試行数'
            default = 50
            note = '3 以上の自然数が有効です。'

        @enum.member
        class mutation_prob(AbstractAlgorithmConfigItem):
            name = '試行ごとの変異確率'
            default = '自動'
            note = '0 から 1 までの数値が有効です。'


# （アルゴリズムごとの）設定値の入力ルール
class NSGAIIAlgorithmDelegate(QStyledItemDelegate):

    def is_population_size(self, index):
        column_data = get_internal_header_data(index)
        row_data = get_internal_header_data(index, Qt.Orientation.Vertical)
        return (
                column_data == QNSGAIIAlgorithmItemModel.ColumnNames.value
                and row_data == NSGAIIAlgorithmConfig.Items.population_size.value.name
        )

    def is_mutation_prob(self, index):
        column_data = get_internal_header_data(index)
        row_data = get_internal_header_data(index, Qt.Orientation.Vertical)
        return (
                column_data == QNSGAIIAlgorithmItemModel.ColumnNames.value
                and row_data == NSGAIIAlgorithmConfig.Items.mutation_prob.value.name
        )

    def setModelData(self, editor, model, index):
        if self.is_population_size(index):
            editor: QLineEdit
            value = editor.text()

            # 3 以上の整数かどうか
            try:
                value = int(value)
                if value < 3:
                    raise ValueError
                value = str(value)

            # そうではないならデフォルト値にする
            except ValueError:
                value = str(NSGAIIAlgorithmConfig.Items.population_size.value.default)

            model.setData(index, value, Qt.ItemDataRole.DisplayRole)

        elif self.is_mutation_prob(index):
            editor: QLineEdit
            value = editor.text()

            # 0 ~ 1 の float であるか
            try:
                value = float(value)
                if value < 0 or 1 < value:
                    raise ValueError
                value = str(value)

            # そうでないならデフォルト値にする
            except ValueError:
                value = str(NSGAIIAlgorithmConfig.Items.mutation_prob.value.default)

            model.setData(index, value, Qt.ItemDataRole.DisplayRole)

        else:
            return super().setModelData(editor, model, index)


# （アルゴリズムごとの）設定項目の ItemModel
class QNSGAIIAlgorithmItemModel(QAbstractAlgorithmItemModel):
    AlgorithmConfig: AbstractAlgorithmConfig = NSGAIIAlgorithmConfig()

    def get_delegate(self):
        return NSGAIIAlgorithmDelegate()

    def output_json(self):
        """
        opt = OptunaOptimizer(
            sampler_class=RandomSampler,
        )
        """

        sampler_kwargs = dict()

        # population_size
        r = self.get_row_by_header_data(NSGAIIAlgorithmConfig.Items.population_size.value.name)
        c = self.get_column_by_header_data(self.ColumnNames.value)
        population_size = int(self.item(r, c).text())
        sampler_kwargs.update({'"population_size"': population_size})

        # mutation_prob
        r = self.get_row_by_header_data(NSGAIIAlgorithmConfig.Items.mutation_prob.value.name)
        c = self.get_column_by_header_data(self.ColumnNames.value)
        mutation_prob = self.item(r, c).text()
        if mutation_prob == NSGAIIAlgorithmConfig.Items.mutation_prob.value.default:
            pass
        else:
            sampler_kwargs.update({'"mutation_prob"': float(mutation_prob)})

        out = dict(
            ret='opt',
            command='OptunaOptimizer',
            args=dict(
                sampler_class='NSGAIISampler',
                sampler_kwargs=sampler_kwargs,
            )
        )

        import json
        return json.dumps([out])


# シングルトンパターン

_MODEL: QNSGAIIAlgorithmItemModel | None = None


def get_nsgaii_algorithm_config_model(parent) -> QNSGAIIAlgorithmItemModel:
    global _MODEL

    if _MODEL is None:
        _MODEL = QNSGAIIAlgorithmItemModel(parent)

    return _MODEL
