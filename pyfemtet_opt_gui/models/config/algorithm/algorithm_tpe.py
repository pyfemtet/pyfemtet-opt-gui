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
class TPEAlgorithmConfig(AbstractAlgorithmConfig):
    name = 'TPE'
    note = 'Optuna 実装に基づくベイズ最適化'

    class Items(enum.Enum):
        @enum.member
        class n_startup_trials(AbstractAlgorithmConfigItem):
            name = 'スタートアップ試行数'
            default = 10
            note = ('TPE アルゴリズムを使う前に必要なランダムにパラメータを\n'
                    '決める試行の回数です。')


# （アルゴリズムごとの）設定値の入力ルール
class TPEAlgorithmDelegate(QStyledItemDelegate):

    def is_n_startup_trials_value(self, index):
        column_data = get_internal_header_data(index)
        row_data = get_internal_header_data(index, Qt.Orientation.Vertical)

        # `n_startup_trials` 行の `value` 列かどうか
        return (
                column_data == QTPEAlgorithmItemModel.ColumnNames.value
                and row_data == TPEAlgorithmConfig.Items.n_startup_trials.value.name
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
                value = str(TPEAlgorithmConfig.Items.n_startup_trials.value.default)

            model.setData(index, value, Qt.ItemDataRole.DisplayRole)

        else:
            return super().setModelData(editor, model, index)


# （アルゴリズムごとの）設定項目の ItemModel
class QTPEAlgorithmItemModel(QAbstractAlgorithmItemModel):
    AlgorithmConfig: AbstractAlgorithmConfig = TPEAlgorithmConfig()

    def get_delegate(self):
        return TPEAlgorithmDelegate()

    def output_json(self):
        """
        opt = OptunaOptimizer(
            sampler_class=RandomSampler,
        )
        """

        r = self.get_row_by_header_data(TPEAlgorithmConfig.Items.n_startup_trials.value.name)
        c = self.get_column_by_header_data(self.ColumnNames.value)
        n_startup_trials = int(self.item(r, c).text())

        out = dict(
            ret='opt',
            command='OptunaOptimizer',
            args=dict(
                sampler_class='TPESampler',
                sampler_kwargs={'"n_startup_trials"': n_startup_trials}
            )
        )

        import json
        return json.dumps([out])


# シングルトンパターン

_MODEL: QTPEAlgorithmItemModel | None = None


def get_tpe_algorithm_config_model(parent) -> QTPEAlgorithmItemModel:
    global _MODEL

    if _MODEL is None:
        _MODEL = QTPEAlgorithmItemModel(parent)

    return _MODEL
