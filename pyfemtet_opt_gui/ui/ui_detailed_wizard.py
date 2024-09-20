from PySide6.QtWidgets import QHeaderView

from pyfemtet_opt_gui.ui.ui_wizard import Ui_Wizard


class Ui_DetailedWizard(Ui_Wizard):

    def setupUi(self, Wizard):
        super().setupUi(Wizard)
        self.tableView_prm.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableView_obj.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableView_cnsList.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.tableView_run.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
