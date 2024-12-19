# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

import enum

from pyfemtet_opt_gui_2.common.common import *
from pyfemtet_opt_gui_2.ui.ui_WizardPage_confirm import Ui_WizardPage
from pyfemtet_opt_gui_2.obj.obj import ObjectiveTableItemModel, get_obj_model

SUB_MODELS = None
PROBLEM_MODEL = None


# ===== rules =====
def get_sub_models() -> dict[str, QStandardItemModel]:
    global SUB_MODELS
    if SUB_MODELS is None:
        SUB_MODELS = dict(
            obj=get_obj_model(),
        )
    return SUB_MODELS


def get_problem_model() -> 'ProblemTableItemModel':
    global PROBLEM_MODEL
    if PROBLEM_MODEL is None:
        PROBLEM_MODEL = ProblemTableItemModel()
    return PROBLEM_MODEL


# ===== objects =====
class ProblemTableItemModel(StandardItemModelWithHeaderSearch):

    sub_models: dict[str, QStandardItemModel]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root = self.invisibleRootItem()
        self.sub_models = get_sub_models()

        with EditModel(self):
            for i, (key, model) in enumerate(self.sub_models.items()):
                item = StandardItemModelAsQStandardItem(key, model)
                self.root.setChild(i, 0, item)
                self.root.setColumnCount(max(
                    self.root.columnCount(),
                    item.columnCount()
                ))

    def flags(self, index):
        return super().flags(index) & ~Qt.ItemFlag.ItemIsEditable & ~Qt.ItemFlag.ItemIsUserCheckable


class ProblemItemModelWithoutUseUnchecked(SortFilterProxyModelOfStandardItemModel):

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):

        # level-0 item. show anyway.
        if not source_parent.isValid():
            return True

        # header row of submodel. show anyway.
        if source_row == 0:
            return True

        # else, get the submodel and its row
        source_model: ProblemTableItemModel = self.sourceModel()
        item: StandardItemModelAsQStandardItem = source_model.itemFromIndex(source_parent)
        sub_model = item.original_model
        sub_model_row = source_row

        # then get the index of `use` cell
        for c in range(sub_model.columnCount()):
            index = sub_model.index(sub_model_row, c)
            if horizontal_header_data_is(index, 'use'):
                break
        else:
            raise RuntimeError('Internal Error!')

        # check checkable
        is_checkable = sub_model.itemFromIndex(index).isCheckable()
        is_checked = sub_model.itemFromIndex(index).checkState() == Qt.CheckState.Checked
        if is_checkable and not is_checked:
            return False

        return super().filterAcceptsRow(source_row, source_parent)


class ConfirmWizardPage(QWizardPage):
    ui: Ui_WizardPage
    source_model: ProblemTableItemModel
    proxy_model: ProblemItemModelWithoutUseUnchecked

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_model()
        self.setup_view()

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)

    def setup_model(self):
        self.source_model = get_problem_model()
        self.proxy_model = ProblemItemModelWithoutUseUnchecked()
        self.proxy_model.setSourceModel(self.source_model)
        self.ui.treeView.setModel(self.proxy_model)

    def setup_view(self):
        view = self.ui.treeView
        view.expandAll()
        for c in range(view.model().columnCount()):
            view.resizeColumnToContents(c)
        view.model().dataChanged.connect(lambda *args: resize_column(view, *args))


if __name__ == '__main__':
    import sys
    from pyfemtet_opt_gui_2.obj.obj import ObjectiveWizardPage

    app = QApplication()
    app.setStyle('fusion')

    page_obj = ObjectiveWizardPage()
    page_obj.show()

    page_main = ConfirmWizardPage()
    page_main.show()

    sys.exit(app.exec())
