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

from pyfemtet_opt_gui_2.models.config.algorithm.base import AlgorithmQStandardItem, AbstractAlgorithmItemModel
from pyfemtet_opt_gui_2.models.config.algorithm.algorithm_random import RandomAlgorithmItemModel, RandomAlgorithmConfig

DEFAULT_ALGORITHM_CONFIG = RandomAlgorithmConfig


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
class ItemColumnNames(enum.StrEnum):
    # use = CommonItemColumnName.use  # 不要、かつ Algorithm とも一貫して見やすい
    name = '項目'
    value = '設定値'
    note = '備考'


class AbstractConfigItem:
    name = ...
    default = ''
    note = ''


class ItemRowNames(enum.Enum):

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
    class algorithm(AbstractConfigItem):
        name = '最適化アルゴリズム'
        default = DEFAULT_ALGORITHM_CONFIG.name


# ===== Models =====
# Delegate
class ConfigTreeViewDelegate(QStyledItemDelegate):

    # FIXME: あとで抽象化する
    partial_model: StandardItemModelWithHeader
    partial_model_delegate: QStyledItemDelegate

    def set_partial_model_delegate(self, partial_model: AbstractAlgorithmItemModel):
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
            editor = self.partial_model_delegate.createEditor(
                parent,
                option,
                self.get_partial_model_index(index)
            )
            return editor

        else:
            # 「最適化アルゴリズム」の「設定値」ならばコンボボックスを作成
            if (
                    get_internal_header_data(index, Qt.Orientation.Vertical) == ItemRowNames.algorithm.value.name
                    and get_internal_header_data(index, Qt.Orientation.Horizontal) == ItemColumnNames.value
            ):
                editor: QComboBox = QComboBox()
                print(editor)
                return editor

            return super().createEditor(parent, option, index)

    # Editor の結果を受けて値を model に反映する
    def setModelData(self, editor, model, index) -> None:
        # model: <__main__.ConfigItemModelForIndividualView(0x21a839c70b0) at 0x0000021A975893C0>

        if self.is_partial_model_item(index):
            self.partial_model_delegate.setModelData(
                editor,
                self.partial_model,  # The change is cloned by signal-slot system.
                self.get_partial_model_index(index)
            )

        else:
            super().setModelData(editor, model, index)

    def setEditorData(self, editor, index) -> None:
        print(editor)
        super().setEditorData(editor, index)

    def paint(self, painter, option, index) -> None:
        super().paint(painter, option, index)

    def sizeHint(self, option, index):
        return super().sizeHint(option, index)


# 大元の ItemModel
class ConfigItemModel(StandardItemModelWithHeader):

    ColumnNames = ItemColumnNames
    RowNames = [enum_item.value.name for enum_item in ItemRowNames]

    def __init__(self, parent=None, _with_dummy=True):

        # setup child items (TODO: あとでリファクタリングする)
        # model = AbstractAlgorithmItemModel(parent, _with_dummy)
        model: AbstractAlgorithmItemModel = RandomAlgorithmItemModel(parent, _with_dummy)

        self.algorithm_config: StandardItemModelAsQStandardItem = \
            AlgorithmQStandardItem(model.name, model)

        self.algorithm_config.setEditable(False)

        super().__init__(parent, _with_dummy)

        if not _with_dummy:
            self.setup_model()

    def _set_dummy_data(self, n_rows=None):
        rows = len(self.RowNames)
        columns = len(self.ColumnNames)

        with EditModel(self):
            self.setRowCount(1 + rows)
            self.setColumnCount(max(columns, self.algorithm_config.columnCount()))

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
            self.setItem(3, 0, self.algorithm_config)

    def setup_model(self):
        rows = len(self.RowNames)
        columns = len(self.ColumnNames)

        with EditModel(self):

            self.setRowCount(1 + rows)
            self.setColumnCount(max(columns, self.algorithm_config.columnCount()))

            # whole table
            item_cls: AbstractConfigItem
            item_cls_list: list[AbstractConfigItem] = [enum_item.value for enum_item in ItemRowNames]
            for r, item_cls in zip(range(1, len(ItemRowNames) + 1), item_cls_list):

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

            # algorithm config table
            with nullcontext():
                # get algorithm row
                r = self.get_row_by_header_data(value=(_enum_item := ItemRowNames.algorithm).value.name)

                # TreeView で child が表示されるのは c==0 のみ
                c = 0

                # overwrite existing item by algorithm config
                self.algorithm_config.setText(ItemRowNames.algorithm.value.name)
                self.setItem(r, c, self.algorithm_config)


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
    proxy_model: ConfigItemModelForProblem
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
        self.ui.treeView.setModel(self.proxy_model)
        self.resize_column()

    def setup_view(self):
        view = self.ui.treeView
        # view.expandAll()  # 初めから Algorithm の設定項目が全部見えたら鬱陶しい
        for c in range(view.model().columnCount()):
            view.resizeColumnToContents(c)
        view.model().dataChanged.connect(lambda *args: resize_column(view, *args))

    def setup_delegate(self):
        # TreeView に対して適用する delegate
        self.delegate = ConfigTreeViewDelegate()

        # StandardItemModelAsQStandardItem を使って
        # TreeView に表示する ItemModel の一部にした
        # AbstractAlgorithmItemModel に対応する delegate を
        # 上記 delegate に適用（上書き）する
        algorithm_item_model: AbstractAlgorithmItemModel = self.source_model.algorithm_config.source_model
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

