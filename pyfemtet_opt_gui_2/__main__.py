# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from pyfemtet_opt_gui_2.femtet.femtet import *
from pyfemtet_opt_gui_2.common.return_msg import *

from pyfemtet_opt_gui_2.ui.ui_Wizard_main import Ui_Wizard
from pyfemtet_opt_gui_2.models.analysis_model.analysis_model import AnalysisModelWizardPage
from pyfemtet_opt_gui_2.models.variables.var import VariableWizardPage
from pyfemtet_opt_gui_2.models.objectives.obj import ObjectiveWizardPage
from pyfemtet_opt_gui_2.models.constraints.cns import ConstraintWizardPage
from pyfemtet_opt_gui_2.models.config.config import ConfigWizardPage
from pyfemtet_opt_gui_2.models.problem.problem import ConfirmWizardPage

import os
import sys
import enum


class ConnectionMessage(enum.StrEnum):
    no_connection = '接続されていません。'
    connecting = '接続中です...'
    connected = '接続されています。'


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
        self.ui.wizardPage_init.isComplete = lambda: get_connection_state() == ReturnMsg.no_message

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

    def connect_femtet(self):
        button: QPushButton = self.ui.pushButton_launch

        # Femtet との接続がすでに OK
        ret: ReturnMsg = get_connection_state()
        if ret == ReturnMsg.no_message:
            self.update_connection_state_label(ConnectionMessage.connected)

        # Femtet との接続が NG
        else:
            # 接続開始
            self.update_connection_state_label(ConnectionMessage.connecting)
            button.setEnabled(False)
            button.repaint()

            # Femtet との接続を開始する
            # Femtet の接続ができるのを待つ
            _, ret_msg = get_femtet()

            # 接続成功
            if ret_msg == ReturnMsg.no_message:
                self.update_connection_state_label(ConnectionMessage.connected)

            # 接続タイムアウト
            else:
                show_return_msg(ret_msg, self)
                self.update_connection_state_label(ConnectionMessage.no_connection)

        # init ページの終了条件を更新する
        self.ui.wizardPage_init.completeChanged.emit()

        # 必要なら sample file を開く
        if (
                get_connection_state() == ReturnMsg.no_message
                and self.ui.checkBox_openSampleFemprj.isChecked()
        ):
            ret_msg, path = self.open_sample_femprj()
            show_return_msg(ret_msg, self, additional_message=path)

        # load_femtet を行う
        self.load_femtet()

        # button を元に戻す
        button.setEnabled(True)
        button.repaint()

    def update_connection_state_label(self, connection_message: ConnectionMessage):
        label: QLabel = self.ui.label_connectionState

        label.setText(connection_message)
        if connection_message == ConnectionMessage.no_connection:
            label.setStyleSheet('color: red')

        elif connection_message == ConnectionMessage.connecting:
            label.setStyleSheet('color: red')

        elif connection_message == ConnectionMessage.connected:
            label.setStyleSheet('color: green')

    def open_sample_femprj(self) -> tuple[ReturnMsg, str]:
        Femtet, ret_msg = get_femtet()

        if ret_msg != ReturnMsg.no_message:
            return ret_msg

        path = os.path.abspath(
                os.path.join(
                    os.path.dirname('__file__'),
                    'assets', 'samples', 'sample.femprj'
                )
            ).replace(os.path.altsep, os.path.sep)
        succeeded = Femtet.LoadProject(path, True)

        if succeeded:
            return ReturnMsg.no_message, path

        else:
            return ReturnMsg.Error.cannot_open_sample_femprj, path

    def load_femtet(self):
        ret_msg = self.am_page.source_model.load_femtet()
        if ret_msg != ReturnMsg.no_message:
            return

        ret_msg = self.var_page.source_model.load_femtet()
        if ret_msg != ReturnMsg.no_message:
            return

        ret_msg = self.obj_page.source_model.load_femtet()
        if ret_msg != ReturnMsg.no_message:
            return


if __name__ == '__main__':

    app = QApplication()
    app.setStyle('fusion')

    page_obj = Main()
    page_obj.show()

    sys.exit(app.exec())
