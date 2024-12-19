# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from pyfemtet_opt_gui_2.ui.ui_Wizard_main import Ui_Wizard
from pyfemtet_opt_gui_2.obj.obj import ObjectiveWizardPage
from pyfemtet_opt_gui_2.problem.problem import ConfirmWizardPage

import sys


class Main(QWizard):
    ui: Ui_Wizard

    def __init__(self, parent=None, flags=Qt.WindowType.Window):
        super().__init__(parent, flags)
        self.setup_ui()
        self.setup_page()

    def setup_ui(self):
        self.ui = Ui_Wizard()
        self.ui.setupUi(self)

    def setup_page(self):
        self.addPage(ObjectiveWizardPage())
        self.addPage(ConfirmWizardPage())


if __name__ == '__main__':

    app = QApplication()
    app.setStyle('fusion')

    page_obj = Main()
    page_obj.show()

    sys.exit(app.exec())
