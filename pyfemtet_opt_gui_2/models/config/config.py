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

from pyfemtet_opt_gui_2.models.config.algorithm.base import (
    QAbstractAlgorithmItemModel,
    AbstractAlgorithmConfig,
    get_abstract_algorithm_config_model,
    QAlgorithmItemModelForProblem,
)

from pyfemtet_opt_gui_2.models.config.algorithm.algorithm_random import (
    get_random_algorithm_config_model,
    RandomAlgorithmConfig,
)

DEFAULT_ALGORITHM_CONFIG = RandomAlgorithmConfig
Q_DEFAULT_ALGORITHM_CONFIG_ITEM_FACTORY = get_random_algorithm_config_model

# ===== model =====
_CONFIG_MODEL = None
_CONFIG_MODEL_FOR_PROBLEM = None
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
    global _CONFIG_MODEL_FOR_PROBLEM
    if _CONFIG_MODEL_FOR_PROBLEM is None:
        assert parent is not None
        source_model = ConfigItemModel(
            parent,
            _WITH_DUMMY if _with_dummy is None else _with_dummy,
            hide_algorithm_note=True,
        )
        _CONFIG_MODEL_FOR_PROBLEM = QConfigItemModelForProblem()
        _CONFIG_MODEL_FOR_PROBLEM.setSourceModel(source_model)
    return _CONFIG_MODEL_FOR_PROBLEM


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
    choices: dict[str, callable] = {
        AbstractAlgorithmConfig.name: get_abstract_algorithm_config_model,
        RandomAlgorithmConfig.name: get_random_algorithm_config_model,
    }


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
class QConfigTreeViewDelegate(QStyledItemDelegateWithCombobox):
    partial_model: QAbstractAlgorithmItemModel
    config_model: 'ConfigItemModel'

    @property
    def partial_model_delegate(self) -> QStyledItemDelegate:
        return self.partial_model.get_delegate()

    @property
    def partial_model(self) -> QAbstractAlgorithmItemModel:
        return Algorithm.choices[self.config_model.get_current_algorithm_item().text()](self.config_model.parent())

    def set_partial_delegate_defined_model(self, config_model: 'ConfigItemModel'):
        self.config_model = config_model

    def is_partial_model_item(self, index: QModelIndex):
        """index が partial model の構成要素の item かどうか"""

        # index の親を取得
        model: QSortFilterProxyModelOfStandardItemModel = index.model()
        assert isinstance(model, QSortFilterProxyModelOfStandardItemModel)
        item = model.sourceModel().itemFromIndex(model.mapToSource(index.parent()))

        # 親が ModelAsItem でなければ partial_model の一部ではない
        # 実装上、親は ModelAsItem にしているはずであるため
        if not isinstance(item, StandardItemModelAsQStandardItem):
            return False

        # 前提として ModelAsItem であれば
        # source か proxy と一致するはず
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
        """
        parent: <PySide6.QtWidgets.QWidget(0x2058a8df940, name="qt_scrollarea_viewport") at 0x000002059BC2A7C0>
        option: < at 0x000002059B2F1B00>
        index: <PySide6.QtCore.QModelIndex(0,1,0x2059a99e230,ConfigItemModelForIndividualView(0x205883e2c60)) at 0x000002059B005BC0>
        """

        # partial model があればまずそれを処理する
        # partial delegate に sizeHint 等を定義した
        # 場合は同様の処理を sizeHint 等に入れる
        if self.is_partial_model_item(index):
            index_ = self.get_partial_model_index(index)
            return self.partial_model_delegate.createEditor(parent, option, index_)

        # 「最適化アルゴリズム」の「設定値」ならばコンボボックスを作成
        # 対応する setModelData, sizeHint, paint は抽象クラスで定義済み
        if self.is_combobox_target(index, 'ALGORITHM'):
            editor = self.create_combobox(
                parent,
                index,
                choices=list(Algorithm.choices.keys()),
                default=DEFAULT_ALGORITHM_CONFIG.name,
            )
            return editor

        # その他の場合
        return super().createEditor(parent, option, index)

    # Editor の結果を受けて値を model に反映する
    def setModelData(self, editor, model, index) -> None:
        """
        # model: <__main__.ConfigItemModelForIndividualView(0x21a839c70b0) at 0x0000021A975893C0>
        """

        # partial_model の場合
        if self.is_partial_model_item(index):
            # The change is cloned by signal-slot system.
            index_ = self.get_partial_model_index(index)
            return self.partial_model_delegate.setModelData(editor, self.partial_model, index_)

        # その他の場合
        super().setModelData(editor, model, index)


# 大元の ItemModel
class ConfigItemModel(StandardItemModelWithHeader):
    ColumnNames = ConfigHeaderNames
    RowNames = [enum_item.value.name for enum_item in ConfigItemClassEnum]

    def __init__(self, parent=None, _with_dummy=True, hide_algorithm_note=False):
        super().__init__(parent, _with_dummy)

        self.hide_algorithm_note = hide_algorithm_note

        # モデルの全体を構築する
        self.setup_model()

        # 既定のアルゴリズムを設定する
        self.algorithm_name = DEFAULT_ALGORITHM_CONFIG.name

        # アルゴリズムを構築する
        self.setup_algorithm(self.algorithm_name)

        # 「最適化アルゴリズム」の「値」が
        # 変わったら ChildItem を切り替える
        self.dataChanged.connect(
            self.check_update_algorithm
        )

    # その時点での「最適化アルゴリズム」の「値」の
    # item を取得する
    def get_current_algorithm_item(self) -> QStandardItem:
        header_data = ConfigItemClassEnum.algorithm.value.name
        r = self.get_row_by_header_data(value=header_data)
        header_data = self.ColumnNames.value
        c = self.get_column_by_header_data(value=header_data)
        item = self.item(r, c)
        return item

    # Item を切り替えるべきか判定し切り替えを行う
    def check_update_algorithm(
            self,
            _top_left: QModelIndex,
            _bottom_right: QModelIndex,
            roles: list[Qt.ItemDataRole],
    ):
        # DisplayRole でアルゴリズムを判断するので
        # それ以外なら何もしない
        if (
                Qt.ItemDataRole.DisplayRole not in roles
                or len(roles) == 0
        ):
            return

        # 現在の algorithm item を取得する
        new_algorithm_name = self.get_current_algorithm_item().text()

        # dataChanged 前までモデルが持っていた
        # はずの algorithm model を取得する
        current_algorithm_name = self.algorithm_name

        # これら二つの名前が同じならば
        # 最適化手法が変更されたわけではない
        if new_algorithm_name == current_algorithm_name:
            return

        # ここまで来たら algorithm name が変更されているので
        # Item を切り替える
        self.setup_algorithm(new_algorithm_name)

    def setup_algorithm(self, algorithm_name):

        with EditModel(self):
            # 「最適化手法」の行番号を取得する
            header_data = ConfigItemClassEnum.algorithm.value.name
            r = self.get_row_by_header_data(value=header_data)

            # TreeView で child が表示されるのは c==0 のみ
            c = 0

            # TreeView での展開情報を格納するためと
            # DisplayRole を「最適化アルゴリズム」に
            # 設定しなおすために itemData を退避する
            item_data: dict = self.itemData(self.index(r, c))
            # print(item_data)  # {0: '最適化アルゴリズム', 13: PySide6.QtCore.QSize(100, 26), 257: True}

            #   ItemModel に紐づかない Item は即座に C++ 内で削除されるが
            # Python 上では ItemModel.dataChanged.connect(Item.do_clone) が
            # 生きているので Item の切り替え後 ItemModel に変更があった場合
            # Python は C++ に古い削除された C++ へのアクセスを試みさせる。
            #   その際に RuntimeError が出る。
            #   古い Item は Python のメモリ上にはあるがロジック上は
            # 使われておらず、切替先の Item では __init__ で別途 dataChanged に
            # connect しているので動作に問題はないが、気持ち悪いので
            # Item の切り替え前に古い C++ QStandardItem オブジェクトへの
            # Connection を切っておく。
            if hasattr(self, '__algorithm_item__'):
                self.__algorithm_item__.proxy_model.dataChanged.disconnect(self.__algorithm_item__.do_clone)

            # 指定された algorithm_name の Model を取得
            if self.hide_algorithm_note:
                _algorithm_model = Algorithm().choices[algorithm_name](self.parent())
                algorithm_model = QAlgorithmItemModelForProblem()
                algorithm_model.setSourceModel(_algorithm_model)
            else:
                algorithm_model = Algorithm().choices[algorithm_name](self.parent())


            # Model から ModelAsItem を作成
            item = StandardItemModelAsQStandardItem(
                text=header_data, model=algorithm_model
            )

            # 切替前に disconnect するために新しい item を保持
            # noinspection PyAttributeOutsideInit
            self.__algorithm_item__ = item

            # Item の置き換え
            self.setItem(r, c, item)

            # Item を置き換えたことをクラスに記憶
            self.algorithm_name = algorithm_name

            # itemData を restore
            # self.setData(self.index(r, c), expanded, role)
            self.setItemData(self.index(r, c), item_data)

    def setup_model(self):
        rows = len(self.RowNames)
        columns = len(self.ColumnNames)

        with EditModel(self):
            self.setRowCount(1 + rows)
            self.setColumnCount(columns)

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
                    item.setText(str(value))
                    self.setItem(r, c, item)

                # note
                with nullcontext():
                    c = self.get_column_by_header_data(self.ColumnNames.note)
                    item: QStandardItem = QStandardItem()
                    item.setEditable(False)
                    item.setText(str(note))
                    self.setItem(r, c, item)


# 一覧 Problem ページに表示される StandardItemModelAsStandardItem 用 ItemModel
class QConfigItemModelForProblem(QSortFilterProxyModelOfStandardItemModel):

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
    delegate: QConfigTreeViewDelegate
    expand_keeper: ExpandStateKeeper
    column_resizer: ResizeColumn

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

        # モデルが更新されたときもその展開状態を維持するようにする
        self.expand_keeper = ExpandStateKeeper(view)

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

        self.column_resizer = ResizeColumn(view)
        self.column_resizer.resize_all_columns()

    def setup_delegate(self):
        # TreeView に対して適用する delegate
        self.delegate = QConfigTreeViewDelegate(self)
        self.delegate.set_partial_delegate_defined_model(
            self.source_model,
        )
        self.delegate.combobox_target_header_data.update(
            {
                'ALGORITHM': (
                    ConfigHeaderNames.value,
                    ConfigItemClassEnum.algorithm.value.name
                )
            }
        )

        # StandardItemModelAsQStandardItem を使って
        # TreeView に表示する ItemModel の一部にした
        # QAbstractAlgorithmItemModel に対応する delegate を
        # 上記 delegate に適用（上書き）する
        self.ui.treeView.setItemDelegate(self.delegate)
        self.column_resizer.resize_all_columns()


if __name__ == '__main__':
    # _WITH_DUMMY = True  # comment out to prevent debug
    # from pyfemtet_opt_gui_2.femtet.mock import get_femtet, get_obj_names  # comment out to prevent debug

    app = QApplication()
    app.setStyle('fusion')

    page_obj = ConfigWizardPage()
    page_obj.show()

    sys.exit(app.exec())
