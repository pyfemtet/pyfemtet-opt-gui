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

from pyfemtet_opt_gui_2.models.analysis_model.analysis_model import get_am_model_for_problem
from pyfemtet_opt_gui_2.models.variables.var import get_var_model_for_problem
from pyfemtet_opt_gui_2.models.objectives.obj import get_obj_model_for_problem
from pyfemtet_opt_gui_2.models.constraints.cns import get_cns_model_for_problem
from pyfemtet_opt_gui_2.models.config.config import get_config_model_for_problem

from pyfemtet_opt_gui_2.builder.main import create_script

SUB_MODELS = None
PROBLEM_MODEL = None


# ===== rules =====
def get_sub_models(parent) -> dict[str, QStandardItemModel]:
    global SUB_MODELS
    if SUB_MODELS is None:
        assert parent is not None
        SUB_MODELS = dict(
            femprj=get_am_model_for_problem(parent=parent),
            parameters=get_var_model_for_problem(parent=parent),
            objectives=get_obj_model_for_problem(parent=parent),
            constraints=get_cns_model_for_problem(parent=parent),
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
    pass


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
        self.setup_signal()

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)

    def setup_model(self):
        self.source_model = get_problem_model(parent=self)
        self.proxy_model = QProblemItemModelWithoutUseUnchecked(self)
        self.proxy_model.setSourceModel(self.source_model)

    def setup_view(self):
        view = self.ui.treeView
        view.setModel(self.proxy_model)
        view.expandAll()

        self.column_resizer = ResizeColumn(view)
        self.column_resizer.resize_all_columns()

    def setup_signal(self):
        # 「スクリプトを保存する」を実行するとスクリプトを保存する
        self.ui.pushButton_save_script.clicked.connect(
            self.save_script
        )

    def save_script(self):
        # 保存ファイル名を決めてもらう
        # キャンセルなら何もしない
        # python モジュールとしての命名規則に従っていなければもう一度
        # create_script
        create_script()
        # 「保存後すぐ実行する」にチェックがあれば実行する
        pass


if __name__ == '__main__':
    import sys
    from pyfemtet_opt_gui_2.femtet.femtet import get_femtet
    from pyfemtet_opt_gui_2.models.objectives.obj import ObjectiveWizardPage
    from pyfemtet_opt_gui_2.models.variables.var import VariableWizardPage
    from pyfemtet_opt_gui_2.models.config.config import ConfigWizardPage
    from pyfemtet_opt_gui_2.models.constraints.cns import ConstraintWizardPage
    from pyfemtet_opt_gui_2.models.analysis_model.analysis_model import AnalysisModelWizardPage

    get_femtet()

    app = QApplication()
    app.setStyle('fusion')

    page_cfg = ConfigWizardPage()
    page_cfg.show()

    page_obj = ObjectiveWizardPage()
    page_obj.show()

    page_var = VariableWizardPage()
    page_var.show()

    page_cns = ConstraintWizardPage()
    page_cns.show()

    page_am = AnalysisModelWizardPage()
    page_am.show()

    page_main = ConfirmWizardPage()
    page_main.show()

    sys.exit(app.exec())
