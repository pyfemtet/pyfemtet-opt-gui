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
import sys
from contextlib import nullcontext

from pyfemtet_opt_gui_2.ui.ui_WizardPage_config import Ui_WizardPage

from pyfemtet_opt_gui_2.common.qt_util import *
from pyfemtet_opt_gui_2.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui_2.common.return_msg import *
from pyfemtet_opt_gui_2.common.expression_processor import *
from pyfemtet_opt_gui_2.femtet.femtet import *

from pyfemtet_opt_gui_2.models.config.algorithm.base import (
    QAlgorithmStandardItem,
    QAbstractAlgorithmItemModel,
    AbstractAlgorithmConfig,
    get_abstract_algorithm_config_item,
)

from pyfemtet_opt_gui_2.models.config.algorithm.algorithm_random import (
    QRandomAlgorithmItemModel,
    get_random_algorithm_config_item,
    RandomAlgorithmConfig,
)

DEFAULT_ALGORITHM_CONFIG = RandomAlgorithmConfig
Q_DEFAULT_ALGORITHM_CONFIG_ITEM_FACTORY = get_random_algorithm_config_item

# ===== model =====
_CONFIG_MODEL = None
_WITH_DUMMY = False


def get_config_model(parent, _with_dummy=None) -> 'ConfigItemModel':
    global _CONFIG_MODEL
    if _CONFIG_MODEL is None:
        assert parent is not None
        _CONFIG_MODEL = ConfigItemModel(
            parent,
            _WITH_DUMMY if _with_dummy is None else _with_dummy,
        )
    return _CONFIG_MODEL


def get_config_model_for_problem(parent, _with_dummy=None):
    model = get_config_model(parent, _with_dummy)
    model_as_item = ConfigItemModelForProblem()
    model_as_item.setSourceModel(model)
    return model_as_item


# ===== constants =====

# 設定項目のヘッダー
class ConfigHeaderNames(enum.StrEnum):
    # use = CommonItemColumnName.use  # 不要、かつ Algorithm とも一貫して見やすい
    name = '項目'
    value = '設定値'
    note = '備考'


# 設定項目のベース
class AbstractConfigItem:
    name = ...
    default = ''
    note = ''


# 設定項目のうちアルゴリズムに関する項目
# 複雑なので切り出し
class Algorithm(AbstractConfigItem):
    name = '最適化アルゴリズム'
    default = DEFAULT_ALGORITHM_CONFIG.name
    choices = [
        AbstractAlgorithmConfig.name,
        RandomAlgorithmConfig.name,
    ]
    corresponding_data = [
        get_abstract_algorithm_config_item,
        get_random_algorithm_config_item,
    ]


# 設定項目の実装
class ConfigItemClassEnum(enum.Enum):
    @enum.member
    class n_trials(AbstractConfigItem):
        name = '解析実行回数'
        default = 10
        note = ''

    @enum.member
    class timeout(AbstractConfigItem):
        name = 'タイムアウト'
        default = 'なし'
        note = ''

    @enum.member
    class algorithm(Algorithm):
        pass


# ===== Models =====

# Delegate
class ConfigTreeViewDelegate(DelegateWithCombobox):
    partial_model: StandardItemModelWithHeader
    partial_model_delegate: QStyledItemDelegate

    def set_partial_model_delegate(self, partial_model: QAbstractAlgorithmItemModel):
        self.partial_model = partial_model
        self.partial_model_delegate = partial_model.get_delegate()

    def is_partial_model_item(self, index: QModelIndex):

        model: SortFilterProxyModelOfStandardItemModel = index.model()
        assert isinstance(model, SortFilterProxyModelOfStandardItemModel)

        item = model.sourceModel().itemFromIndex(model.mapToSource(index.parent()))

        # Is item a StandardItemModelAsQStandardItem or not
        if not isinstance(item, StandardItemModelAsQStandardItem):
            return False

        # If item is StandardItemModelAsQStandardItem,
        # is the 大元 model a partial_model or not.
        item: StandardItemModelAsQStandardItem
        if (
                (id(item.source_model) == id(self.partial_model))
                or (id(item.proxy_model) == id(self.partial_model))
        ):
            return True

        # item is not a target model.
        return False

    def get_partial_model_index(self, index):
        return self.partial_model.index(index.row(), index.column())

    # Editor の定義
    def createEditor(self, parent, option, index):
        # parent: <PySide6.QtWidgets.QWidget(0x2058a8df940, name="qt_scrollarea_viewport") at 0x000002059BC2A7C0>
        # option: < at 0x000002059B2F1B00>
        # index: <PySide6.QtCore.QModelIndex(0,1,0x2059a99e230,ConfigItemModelForIndividualView(0x205883e2c60)) at 0x000002059B005BC0>

        # partial model があればまずそれを処理する
        if self.is_partial_model_item(index):
            index_ = self.get_partial_model_index(index)
            return self.partial_model_delegate.createEditor(parent, option, index_)

        else:
            # 「最適化アルゴリズム」の「設定値」ならばコンボボックスを作成
            if (
                    get_internal_header_data(index, Qt.Orientation.Vertical) == ConfigItemClassEnum.algorithm.value.name
                    and get_internal_header_data(index, Qt.Orientation.Horizontal) == ConfigHeaderNames.value
            ):
                editor = self.create_combobox(
                    parent,
                    index,
                    choices=Algorithm.choices,
                    default=DEFAULT_ALGORITHM_CONFIG.name,
                )

                return editor

            return super().createEditor(parent, option, index)

    # Editor の結果を受けて値を model に反映する
    def setModelData(self, editor, model, index) -> None:
        # model: <__main__.ConfigItemModelForIndividualView(0x21a839c70b0) at 0x0000021A975893C0>

        if self.is_partial_model_item(index):
            # The change is cloned by signal-slot system.
            index_ = self.get_partial_model_index(index)
            self.partial_model_delegate.setModelData(editor, self.partial_model, index_)

        else:
            super().setModelData(editor, model, index)

    def setEditorData(self, editor, index) -> None:
        super().setEditorData(editor, index)

    def paint(self, painter, option, index) -> None:
        if (
                get_internal_header_data(index, Qt.Orientation.Vertical) == ConfigItemClassEnum.algorithm.value.name
                and get_internal_header_data(index, Qt.Orientation.Horizontal) == ConfigHeaderNames.value
        ):
            return self.paint_as_combobox(painter, option, index)

        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        if (
                get_internal_header_data(index, Qt.Orientation.Vertical) == ConfigItemClassEnum.algorithm.value.name
                and get_internal_header_data(index, Qt.Orientation.Horizontal) == ConfigHeaderNames.value
        ):
            return self.get_combobox_size_hint(option, index)

        return super().sizeHint(option, index)


# 大元の ItemModel
class ConfigItemModel(StandardItemModelWithHeader):
    ColumnNames = ConfigHeaderNames
    RowNames = [enum_item.value.name for enum_item in ConfigItemClassEnum]
    q_algorithm_item: QAlgorithmStandardItem

    def __init__(self, parent=None, _with_dummy=True):

        self.q_algorithm_item = Q_DEFAULT_ALGORITHM_CONFIG_ITEM_FACTORY(parent)

        super().__init__(parent, _with_dummy)

        if not _with_dummy:
            self.setup_model()

    def _set_dummy_data(self, n_rows=None):
        rows = len(self.RowNames)
        columns = len(self.ColumnNames)

        with EditModel(self):
            self.setRowCount(1 + rows)
            self.setColumnCount(
                max(columns, self.q_algorithm_item.columnCount())
            )

            # ツリー構造の作成
            item01 = QStandardItem(get_internal_header_data(self.index(0, 0)))
            item02 = QStandardItem(get_internal_header_data(self.index(0, 1)))

            item11 = QStandardItem('item11')
            item12 = QStandardItem('item12')

            item21 = QStandardItem('item21')
            item22 = QStandardItem('item22')

            # 最終的にモデルに追加する
            self.setItem(0, 0, item01)
            self.setItem(0, 1, item02)
            self.setItem(1, 0, item11)
            self.setItem(1, 1, item12)
            self.setItem(2, 0, item21)
            self.setItem(2, 1, item22)
            self.setItem(3, 0, self.q_algorithm_item)

    def setup_algorithm(self):
        rows = len(self.RowNames)
        columns = len(self.ColumnNames)

        # algorithm config table
        with EditModel(self):
            self.setRowCount(1 + rows)
            self.setColumnCount(max(columns, self.q_algorithm_item.columnCount()))

            # get algorithm row
            r = self.get_row_by_header_data(value=(_enum_item := ConfigItemClassEnum.algorithm).value.name)

            # TreeView で child が表示されるのは c==0 のみ
            c = 0

            # overwrite existing item by algorithm config
            self.q_algorithm_item.setText(ConfigItemClassEnum.algorithm.value.name)

            # apply change
            self.setItem(r, c, self.q_algorithm_item)

    def setup_model(self):
        rows = len(self.RowNames)
        columns = len(self.ColumnNames)

        with EditModel(self):
            self.setRowCount(1 + rows)
            self.setColumnCount(max(columns, self.q_algorithm_item.columnCount()))

            # whole table
            item_cls: AbstractConfigItem
            item_cls_list: list[AbstractConfigItem] = [enum_item.value for enum_item in ConfigItemClassEnum]
            for r, item_cls in zip(range(1, len(ConfigItemClassEnum) + 1), item_cls_list):
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
                    print(value)
                    item.setText(str(value))
                    self.setItem(r, c, item)

                # note
                with nullcontext():
                    c = self.get_column_by_header_data(self.ColumnNames.note)
                    item: QStandardItem = QStandardItem()
                    item.setEditable(False)
                    item.setText(str(note))
                    self.setItem(r, c, item)

        self.setup_algorithm()


# 一覧 Problem ページに表示される StandardItemModelAsStandardItem 用 ItemModel
class ConfigItemModelForProblem(SortFilterProxyModelOfStandardItemModel):

    def filterAcceptsColumn(self, source_column: int, source_parent: QModelIndex):
        # note を非表示
        source_model: ConfigItemModel = self.sourceModel()
        if source_column == get_column_by_header_data(
                source_model,
                ConfigItemModel.ColumnNames.note
        ):
            return False

        return True


# 個別ページに表示される first row のない ItemModel
class ConfigItemModelForIndividualView(StandardItemModelWithoutFirstRow):
    pass


class ConfigWizardPage(QWizardPage):
    ui: Ui_WizardPage
    source_model: ConfigItemModel
    proxy_model: ConfigItemModelForIndividualView
    delegate: ConfigTreeViewDelegate

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_model()
        self.setup_view()
        self.setup_delegate()

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)

    def setup_model(self):
        self.source_model = get_config_model(self)
        self.proxy_model = ConfigItemModelForIndividualView(self)
        self.proxy_model.setSourceModel(self.source_model)

    def setup_view(self):
        view = self.ui.treeView
        view.setModel(self.proxy_model)
        # view.expandAll()  # 初めから Algorithm の設定項目が全部見えたら鬱陶しい

        # direction 列のみシングルクリックでコンボボックスが
        # 開くようにシングルクリックで edit モードに入るよう
        # にする
        view.clicked.connect(
            lambda *args, **kwargs: start_edit_specific_column(
                self.ui.treeView.edit,
                ConfigHeaderNames.value,
                *args,
            )
        )

        for c in range(view.model().columnCount()):
            view.resizeColumnToContents(c)
        view.model().dataChanged.connect(lambda *args: resize_column(view, *args))

    def setup_delegate(self):
        # TreeView に対して適用する delegate
        self.delegate = ConfigTreeViewDelegate(self)

        # StandardItemModelAsQStandardItem を使って
        # TreeView に表示する ItemModel の一部にした
        # QAbstractAlgorithmItemModel に対応する delegate を
        # 上記 delegate に適用（上書き）する
        algorithm_item_model: QAbstractAlgorithmItemModel = self.source_model.q_algorithm_item.source_model
        self.delegate.set_partial_model_delegate(algorithm_item_model)
        self.ui.treeView.setItemDelegate(self.delegate)
        self.resize_column()

    def resize_column(self):
        items = []
        for r in range(self.source_model.rowCount()):
            for c in range(self.source_model.columnCount()):
                items.append(self.source_model.item(r, c))
        resize_column(self.ui.treeView, *items)


if __name__ == '__main__':
    # _WITH_DUMMY = True  # comment out to prevent debug
    # from pyfemtet_opt_gui_2.femtet.mock import get_femtet, get_obj_names  # comment out to prevent debug

    app = QApplication()
    app.setStyle('fusion')

    page_obj = ConfigWizardPage()
    page_obj.show()

    sys.exit(app.exec())
