# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from pyfemtet_opt_gui_2.ui.ui_WizardPage_confirm import Ui_WizardPage
from pyfemtet_opt_gui_2.common.qt_util import *
from pyfemtet_opt_gui_2.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui_2.models.objectives.obj import get_obj_model_for_problem
from pyfemtet_opt_gui_2.models.variables.var import get_var_model_for_problem
from pyfemtet_opt_gui_2.models.config.config import get_config_model_for_problem

SUB_MODELS = None
PROBLEM_MODEL = None


# ===== rules =====
def get_sub_models(parent) -> dict[str, QStandardItemModel]:
    global SUB_MODELS
    if SUB_MODELS is None:
        assert parent is not None
        SUB_MODELS = dict(
            objectives=get_obj_model_for_problem(parent=parent),
            parameters=get_var_model_for_problem(parent=parent),
            config=get_config_model_for_problem(parent=parent),
        )
    return SUB_MODELS


def get_problem_model(parent=None) -> 'ProblemTableItemModel':
    global PROBLEM_MODEL
    if PROBLEM_MODEL is None:
        PROBLEM_MODEL = ProblemTableItemModel(parent=parent)
    return PROBLEM_MODEL


# ===== objects =====
class ProblemTableItemModel(StandardItemModelWithEnhancedFirstRow):
    sub_models: dict[str, QStandardItemModel]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root = self.invisibleRootItem()
        self.sub_models = get_sub_models(parent=parent)

        with EditModel(self):

            # 各サブモデルごとに setChild する
            for i, (key, model) in enumerate(self.sub_models.items()):

                # item に変換
                item = StandardItemModelAsQStandardItem(key, model)

                # setChild
                self.root.setChild(i, 0, item)

                # カラム数をサブモデルの最大値に設定
                self.root.setColumnCount(
                    max(
                        self.root.columnCount(),
                        item.columnCount()
                    )
                )

    def flags(self, index):
        return super().flags(index) & ~Qt.ItemFlag.ItemIsEditable & ~Qt.ItemFlag.ItemIsUserCheckable


class QProblemItemModelWithoutUseUnchecked(QSortFilterProxyModelOfStandardItemModel):

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):

        # root item. show anyway.
        if not source_parent.isValid():
            return True

        # header row of submodel. show anyway.
        if source_row == 0:
            return True

        # else, get the submodel and its row.
        source_model: ProblemTableItemModel = self.sourceModel()

        # First get the ModelAsItem to get sub-model header information.
        item = source_model.itemFromIndex(source_parent)

        # If the item is not StandardItemModelAsQStandardItem,
        # We are processing a child of QStandardItem or
        # do_cloned nested ModelAsItem (what behaves as a QStandardItem).
        # Now we cannot access to header data and
        # 現在のところ孫以降の階層で詳細に制御するべきデータがないので
        # この場合は super クラスに処理を任せる。
        # もしここを実装したい場合は ModelAsItem の do_clone の
        # children の clone の処理の直後に CustomUserRole でも定義
        # すればいいと思われる。
        if not isinstance(item, StandardItemModelAsQStandardItem):
            return super().filterAcceptsRow(source_row, source_parent)

        item: StandardItemModelAsQStandardItem
        sub_proxy_model = item.proxy_model  # model of ModelAsItem
        sub_proxy_model_row = source_row  # row of item.proxy_model
        assert isinstance(sub_proxy_model.sourceModel(), StandardItemModelWithHeader)
        sub_source_model: StandardItemModelWithHeader = sub_proxy_model.sourceModel()

        # If the sub-model doesn't have
        # `use` header, show it (or not).
        if CommonItemColumnName.use not in sub_source_model.ColumnNames:
            return super().filterAcceptsRow(source_row, source_parent)

        # then get the index of `use` cell
        sub_proxy_index = get_column_by_header_data(
            sub_proxy_model, CommonItemColumnName.use, sub_proxy_model_row
        )

        # check checkable
        sub_source_model = sub_proxy_model.sourceModel()
        sub_source_index = sub_proxy_model.mapToSource(sub_proxy_index)
        is_checkable = sub_source_model.itemFromIndex(sub_source_index).isCheckable()
        is_checked = sub_source_model.itemFromIndex(sub_source_index).checkState() == Qt.CheckState.Checked
        if is_checkable and not is_checked:
            return False

        return super().filterAcceptsRow(source_row, source_parent)


class ConfirmWizardPage(QWizardPage):
    ui: Ui_WizardPage
    source_model: ProblemTableItemModel
    proxy_model: QProblemItemModelWithoutUseUnchecked
    column_resizer: ResizeColumn

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_model()
        self.setup_view()

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)

    def setup_model(self):
        self.source_model = get_problem_model(parent=self)
        self.proxy_model = QProblemItemModelWithoutUseUnchecked()
        self.proxy_model.setSourceModel(self.source_model)

    def setup_view(self):
        view = self.ui.treeView
        view.setModel(self.proxy_model)
        view.expandAll()

        self.column_resizer = ResizeColumn(view)
        self.column_resizer.resize_all_columns()



if __name__ == '__main__':
    import sys
    from pyfemtet_opt_gui_2.femtet.femtet import get_femtet
    from pyfemtet_opt_gui_2.models.objectives.obj import ObjectiveWizardPage
    from pyfemtet_opt_gui_2.models.variables.var import VariableWizardPage
    from pyfemtet_opt_gui_2.models.config.config import ConfigWizardPage

    get_femtet()

    app = QApplication()
    app.setStyle('fusion')

    page_cfg = ConfigWizardPage()
    page_cfg.show()

    page_obj = ObjectiveWizardPage()
    page_obj.show()

    page_var = VariableWizardPage()
    page_var.show()

    page_main = ConfirmWizardPage()
    page_main.show()

    sys.exit(app.exec())
