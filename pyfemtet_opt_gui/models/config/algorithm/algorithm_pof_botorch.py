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
class PoFBoTorchAlgorithmConfig(AbstractAlgorithmConfig):
    name = 'PoFBoTorch'
    note = '実行可能性考慮付きガウス過程回帰ベイズ最適化'

    class Items(enum.Enum):
        @enum.member
        class n_startup_trials(AbstractAlgorithmConfigItem):
            name = 'スタートアップ試行数'
            default = 10
            note = ('PoFBoTorch アルゴリズムを使う前に必要なランダムにパラメータを\n'
                    '決める試行の回数です。')


# （アルゴリズムごとの）設定値の入力ルール
class PoFBoTorchAlgorithmDelegate(QStyledItemDelegate):

    def is_n_startup_trials_value(self, index):
        column_data = get_internal_header_data(index)
        row_data = get_internal_header_data(index, Qt.Orientation.Vertical)

        # `n_startup_trials` 行の `value` 列かどうか
        return (
                column_data == QPoFBoTorchAlgorithmItemModel.ColumnNames.value
                and row_data == PoFBoTorchAlgorithmConfig.Items.n_startup_trials.value.name
        )

    def setModelData(self, editor, model, index):
        if self.is_n_startup_trials_value(index):
            editor: QLineEdit
            value = editor.text()

            # 1 以上の整数かどうか
            try:
                value = int(value)
                if value < 1:
                    raise ValueError
                value = str(value)

            # 1 以上の整数ではないならデフォルト値にする
            except ValueError:
                value = str(PoFBoTorchAlgorithmConfig.Items.n_startup_trials.value.default)

            model.setData(index, value, Qt.ItemDataRole.DisplayRole)

        else:
            return super().setModelData(editor, model, index)


# （アルゴリズムごとの）設定項目の ItemModel
class QPoFBoTorchAlgorithmItemModel(QAbstractAlgorithmItemModel):
    AlgorithmConfig: AbstractAlgorithmConfig = PoFBoTorchAlgorithmConfig()

    def get_delegate(self):
        return PoFBoTorchAlgorithmDelegate()

    def output_json(self):
        """
        opt = OptunaOptimizer(
            sampler_class=RandomSampler,
        )
        """

        r = self.get_row_by_header_data(PoFBoTorchAlgorithmConfig.Items.n_startup_trials.value.name)
        c = self.get_column_by_header_data(self.ColumnNames.value)
        n_startup_trials = int(self.item(r, c).text())

        out = dict(
            ret='opt',
            command='OptunaOptimizer',
            args=dict(
                sampler_class='PoFBoTorchSampler',
                sampler_kwargs={'"n_startup_trials"': n_startup_trials}
            )
        )

        import json
        return json.dumps([out])


# シングルトンパターン

_MODEL: QPoFBoTorchAlgorithmItemModel | None = None


def get_pof_botorch_algorithm_config_model(parent) -> QPoFBoTorchAlgorithmItemModel:
    global _MODEL

    if _MODEL is None:
        _MODEL = QPoFBoTorchAlgorithmItemModel(parent)

    return _MODEL
