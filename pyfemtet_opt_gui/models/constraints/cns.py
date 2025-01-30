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

from pyfemtet_opt_gui.ui.ui_WizardPage_cns import Ui_WizardPage

from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui.common.return_msg import *
from pyfemtet_opt_gui.common.titles import *
from pyfemtet_opt_gui.femtet.femtet import *

from pyfemtet_opt_gui.models.constraints.model import get_cns_model, ConstraintModel
from pyfemtet_opt_gui.models.constraints.cns_dialog import ConstraintEditorDialog

import enum
import sys
from contextlib import nullcontext


def get_cns_model_for_problem(parent, _with_dummy=None):
    model = get_cns_model(parent, _with_dummy)
    model_for_problem = ConstraintModelForProblem(parent)
    model_for_problem.setSourceModel(model)
    return model_for_problem


class ConstraintModelForProblem(ProxyModelWithForProblem):
    pass


# hide 1st row
class ConstraintModelWithoutFirstRow(StandardItemModelWithoutFirstRow):
    pass


# UI
class ConstraintWizardPage(TitledWizardPage):
    ui: Ui_WizardPage
    source_model: ConstraintModel
    proxy_model: ConstraintModelWithoutFirstRow
    column_resizer: ResizeColumn
    view: QTableView

    page_name = PageSubTitles.cns

    def __init__(self, parent=None, load_femtet_fun=None):
        super().__init__(parent)
        self.load_femtet_fun = load_femtet_fun
        self.setup_ui()
        self.setup_model()
        self.setup_view()
        self.setup_signal()

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)

    def setup_model(self):
        self.source_model = get_cns_model(parent=self)
        self.proxy_model = ConstraintModelWithoutFirstRow(self)
        self.proxy_model.setSourceModel(self.source_model)

    def setup_view(self):
        view = self.ui.tableView_cnsList
        view.setModel(self.proxy_model)
        self.view = view

        self.column_resizer = ResizeColumn(view)
        self.column_resizer.resize_all_columns()

    def setup_signal(self):
        self.ui.pushButton_add.clicked.connect(
            lambda _: self.open_dialog()
        )

        self.ui.pushButton_edit.clicked.connect(
            lambda _: self.open_dialog(self.get_selected_name())
        )

    def get_selected_name(self) -> str | None:
        proxy_indexes = self.view.selectedIndexes()
        if len(proxy_indexes) == 0:
            return None

        proxy_index: QModelIndex = proxy_indexes[0]

        assert isinstance(proxy_index.model(), ConstraintModelWithoutFirstRow)
        proxy_model: ConstraintModelWithoutFirstRow = proxy_index.model()

        assert isinstance(proxy_model.sourceModel(), ConstraintModel)
        source_model: ConstraintModel = proxy_model.sourceModel()
        source_index = proxy_model.mapToSource(proxy_index)

        r = source_index.row()
        c = source_model.get_column_by_header_data(source_model.ColumnNames.name)

        return source_model.item(r, c).text()

    def open_dialog(self, name=None):
        dialog = ConstraintEditorDialog(
            parent=self,
            existing_constraint_name=name,
            load_femtet_fun=self.load_femtet_fun
        )
        dialog.show()


if __name__ == '__main__':
    app = QApplication()
    app.setStyle('fusion')
    window = ConstraintWizardPage()
    window.show()
    app.exec()
