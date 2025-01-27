# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from pyfemtet_opt_gui.ui.ui_WizardPage_confirm import Ui_WizardPage
from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui.common.return_msg import *

from pyfemtet_opt_gui.models.analysis_model.analysis_model import get_am_model_for_problem
from pyfemtet_opt_gui.models.variables.var import get_var_model_for_problem
from pyfemtet_opt_gui.models.objectives.obj import get_obj_model_for_problem
from pyfemtet_opt_gui.models.constraints.cns import get_cns_model_for_problem
from pyfemtet_opt_gui.models.config.config import get_config_model_for_problem

from pyfemtet_opt_gui.builder.main import create_script
from pyfemtet_opt_gui.builder.file_dialog import ScriptBuilderFileDialog
from pyfemtet_opt_gui.builder.worker import OptimizationWorker

import requests
from requests.exceptions import ConnectionError
from packaging.version import Version

import pyfemtet

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
    worker: OptimizationWorker

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
        selected_file = None
        while True:
            # ダイアログを作成
            dialog = ScriptBuilderFileDialog(parent=self)

            # 以前の file 名指定が残っていれば復元
            if selected_file is not None:
                dialog.selectFile(selected_file)

            # ダイアログを実行（modal, blocking)
            dialog.exec()

            # ファイルパスを取得 (長さ 0 or 1)
            selected_files = dialog.selectedFiles()

            # 命名違反でなければ抜ける
            if can_continue(dialog.return_msg, self):
                break

            # 命名違反であれば selected_file を保存してもう一度
            else:
                assert len(selected_files) != 0
                selected_file = selected_files[0]

        # 保存ファイル名が指定しなければ
        # キャンセルと見做して何もしない
        if len(selected_files) == 0:
            return

        # スクリプトを保存する
        path = selected_files[0]
        create_script(path)

        # 「保存後すぐ実行する」にチェックがあれば実行する
        should_run = self.ui.checkBox_save_with_run.checkState() == Qt.CheckState.Checked
        if should_run:
            self.run_script(path)

    def run_script(self, path):
        self.worker = OptimizationWorker(self.parent(), path)
        self.worker.started.connect(lambda: self.switch_button(True))
        self.worker.finished.connect(lambda: self.switch_button(False))
        self.worker.start()

    def switch_button(self, running: bool):
        # worker が実行ならば button を disabled にするなど
        button = self.ui.pushButton_save_script

        if Version(pyfemtet.__version__) >= Version("0.8.5"):
            if running:
                button.clicked.disconnect(self.save_script)
                button.clicked.connect(self.stop_optimization)
                button.setText('現在の解析を最後にして最適化を停止する')
            else:
                # 元に戻す
                button.clicked.disconnect(self.stop_optimization)
                button.clicked.connect(self.save_script)
                button.setText(button.accessibleName())

                # history_path の情報を model から消す（初期化）
                model = get_config_model_for_problem(self)
                model.reset_history_path()

        else:
            if running:
                button.setText('最適化の実行中はスクリプトを保存できません')
                button.setDisabled(True)
            else:
                # 元に戻す
                button.setText(button.accessibleName())
                button.setDisabled(False)

    def stop_optimization(self):
        # port record が存在するかチェックする
        proxy_model = get_config_model_for_problem(self)

        # 最新版にアップデートしなければ使えない
        # またはまだ最適化が始まっていない
        host_info, ret_msg = proxy_model.get_monitor_host_info()
        if not can_continue(ret_msg, parent=self):
            return

        host = host_info['host']
        port = host_info['port']

        try:
            response = requests.get(f'http://{host}:{port}/interrupt')

            # info をメッセージする
            if response.status_code == 200:
                # print("Success:", response.json())
                ret_msg = ReturnMsg.Info.interrupt_signal_emitted
                show_return_msg(ret_msg, parent=self)

            # error をメッセージする
            else:
                # print("Failed to execute command.")
                ret_msg = ReturnMsg.Error.failed_to_emit_interrupt_signal
                show_return_msg(ret_msg, parent=self)

        # error をメッセージする
        except ConnectionError:
            # print("Failed to connect server.")
            ret_msg = ReturnMsg.Error.failed_to_connect_process_monitor
            show_return_msg(ret_msg, parent=self)


if __name__ == '__main__':
    import sys
    from pyfemtet_opt_gui.femtet.femtet import get_femtet
    from pyfemtet_opt_gui.models.objectives.obj import ObjectiveWizardPage
    from pyfemtet_opt_gui.models.variables.var import VariableWizardPage
    from pyfemtet_opt_gui.models.config.config import ConfigWizardPage
    from pyfemtet_opt_gui.models.constraints.cns import ConstraintWizardPage
    from pyfemtet_opt_gui.models.analysis_model.analysis_model import AnalysisModelWizardPage

    get_femtet()

    app = QApplication()
    app.setStyle('fusion')

    # page_cfg = ConfigWizardPage()
    # page_cfg.show()
    #
    # page_obj = ObjectiveWizardPage()
    # page_obj.show()
    #
    # page_var = VariableWizardPage()
    # page_var.show()
    #
    # page_cns = ConstraintWizardPage()
    # page_cns.show()
    #
    # page_am = AnalysisModelWizardPage()
    # page_am.show()

    page_main = ConfirmWizardPage()
    page_main.show()

    sys.exit(app.exec())
