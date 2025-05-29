import sys

# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

import pyfemtet_opt_gui

print('=== pyfemtet_opt_gui version', pyfemtet_opt_gui.__version__, '===')
print('Loading modules. It can take a few minutes for first time...')

from pyfemtet_opt_gui.ui.ui_Wizard_main import Ui_Wizard
from pyfemtet_opt_gui.models.analysis_model.analysis_model import AnalysisModelWizardPage
from pyfemtet_opt_gui.models.variables.var import VariableWizardPage
from pyfemtet_opt_gui.models.objectives.obj import ObjectiveWizardPage
from pyfemtet_opt_gui.models.constraints.cns import ConstraintWizardPage
from pyfemtet_opt_gui.models.config.config import ConfigWizardPage
from pyfemtet_opt_gui.models.problem.problem import ConfirmWizardPage

from pyfemtet_opt_gui.common.return_msg import *
from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.fem_interfaces.connection_worker import *

import pyfemtet_opt_gui.fem_interfaces as fi

# Necessary to import early timing.
# (importing just before run or threading causes an error.)
# noinspection PyUnresolvedReferences
import torch


class Main(QWizard):
    ui: Ui_Wizard
    am_page: 'AnalysisModelWizardPage'
    var_page: 'VariableWizardPage'
    obj_page: 'ObjectiveWizardPage'
    cns_page: 'ConstraintWizardPage'
    config_page: 'ConfigWizardPage'
    problem_page: 'ConfirmWizardPage'

    def __init__(self, parent=None, flags=Qt.WindowType.Window):
        super().__init__(parent, flags)
        self.setup_ui()
        self.setup_page()

    def setup_ui(self):
        self.ui = Ui_Wizard()
        self.ui.setupUi(self)

        # Connect Femtet button
        self.ui.pushButton_launch.clicked.connect(self.connect_femtet)

        # Cannot go to next page without connection
        self.ui.wizardPage_init.isComplete = lambda: fi.get().get_connection_state() == ReturnMsg.no_message

        # Setup CAD integration
        self.ui.comboBox.addItems([txt for txt in fi.CADIntegration])
        self.ui.comboBox.setCurrentIndex(0)
        self.ui.comboBox.currentTextChanged.connect(self.switch_cad)

    def setup_page(self):
        self.am_page = AnalysisModelWizardPage(self, load_femtet_fun=self.load_femtet)
        self.var_page = VariableWizardPage(self, load_femtet_fun=self.load_femtet)
        self.obj_page = ObjectiveWizardPage(self, load_femtet_fun=self.load_femtet)
        self.cns_page = ConstraintWizardPage(self, load_femtet_fun=self.load_femtet)
        self.config_page = ConfigWizardPage(self)
        self.problem_page = ConfirmWizardPage(self)

        self.addPage(self.am_page)
        self.addPage(self.var_page)
        self.addPage(self.obj_page)
        self.addPage(self.cns_page)
        self.addPage(self.config_page)
        self.addPage(self.problem_page)

    def switch_cad(self, cad):
        fi.switch_cad(cad)

    def connect_femtet(self):
        """
        プロセスとの接続は必要時間がわからないのでスレッド化して
        プログレスバーのアニメーションで作業中であることを示す

        Qt モデルの更新はメインスレッドでないと動作しないので
        接続が終わり次第メインスレッドで更新するが
        このときプログレスバーを更新することで作業中であることを示す
        """

        button: QPushButton = self.ui.pushButton_launch

        # progress を準備する
        progress = UntouchableProgressDialog('Working...', '', 0, 0, parent=self)
        progress.setWindowTitle('status')
        progress.show()

        # 開始時及び終了時の動作を定義する
        def when_start():

            # button を disable にする
            button.setEnabled(False)
            button.repaint()

        def when_finished(ret_code):

            # init ページの終了条件を更新する
            self.ui.wizardPage_init.completeChanged.emit()

            # connection に成功したかどうか
            if can_continue(ret_code, self, no_dialog_if_info=True):

                # スレッドで接続に成功していても
                # 一度は メインスレッドで接続しなければならない
                fi.get().get_femtet()

                # load_femtet を行う
                # 時間がかかるが Model の更新は
                # メインスレッドで行う必要がある？
                self.load_femtet(progress)

            # button を元に戻す
            button.setEnabled(True)
            button.repaint()

            # progress を消す
            progress.cancel()

        # 接続を開始する
        task = ConnectionWorker(self, self.ui, progress)
        task.started.connect(when_start)
        task.finished.connect(lambda ret_code: when_finished(ret_code))
        task.start()

    def load_femtet(self, progress: QProgressDialog = None):

        if progress is not None:
            progress.setMinimum(0)
            progress.setMaximum(6)
            progress.show()

        if progress is not None:
            progress.setLabelText('ファイル情報を読み込んでいます...')
            progress.setValue(progress.value() + 1)
            progress.forceShow()
        ret_msg = self.am_page.source_model.load_femtet(progress)  # progress +3
        if ret_msg != ReturnMsg.no_message:
            return

        if progress is not None:
            progress.setLabelText('変数を読み込んでいます...')
            progress.setValue(progress.value() + 1)
            progress.forceShow()
        ret_msg = self.var_page.source_model.load_femtet()
        if ret_msg != ReturnMsg.no_message:
            return

        if progress is not None:
            progress.setLabelText('解析設定を読み込んでいます...')
            progress.setValue(progress.value() + 1)
            progress.forceShow()
        ret_msg = self.obj_page.source_model.load_femtet()
        if ret_msg != ReturnMsg.no_message:
            return


def main():
    print('Module loaded. Initializing...')
    app = QApplication()
    app.setStyle('fusion')

    page_obj = Main()
    page_obj.show()
    print('pyfemtet-opt-gui successfully launched!')

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
