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

from pyfemtet_opt_gui_2.ui.ui_WizardPage_obj import Ui_WizardPage_obj

from pyfemtet_opt_gui_2.common.common import *

ICON_PATH = r'pyfemtet-opt-gui\pyfemtet_opt_gui_2\assets\icon\arrow.svg'

# ===== model =====
OBJ_MODEL = None


def get_obj_model() -> 'ObjectiveTableItemModel':
    global OBJ_MODEL
    if OBJ_MODEL is None:
        OBJ_MODEL = ObjectiveTableItemModel()
    return OBJ_MODEL


# ===== constants =====
class ObjectiveColumnNames(enum.StrEnum):
    use = 'use'
    name = 'name'
    data = 'data',
    direction = 'direction',
    target_value = 'target',


class ObjectiveDirection(enum.StrEnum):  # python >= 3.11
    minimize = 'minimize'
    maximize = 'maximize'
    specific_value = 'aim for'


# ===== qt objects =====
class ObjectiveItemDelegate(StyledItemDelegateWithHeaderSearch):

    def create_combobox(self, parent, default_value=None):
        cb = QComboBox(parent)
        cb.addItems([p for p in ObjectiveDirection])
        if default_value is not None:
            cb.setCurrentText(default_value)  # 選択肢になければ無視される模様
        cb.setFrame(False)
        return cb

    def createEditor(self, parent, option, index):
        if self.horizontal_header_data_is(index, ObjectiveColumnNames.direction):
            cb = self.create_combobox(parent, default_value=index.model().data(index, Qt.ItemDataRole.DisplayRole))
            QTimer.singleShot(0, cb.showPopup)
            return cb

        elif self.horizontal_header_data_is(index, ObjectiveColumnNames.use):
            return None

        elif self.horizontal_header_data_is(index, ObjectiveColumnNames.target_value):
            editor: QLineEdit = super().createEditor(parent, option, index)
            double_validator = QDoubleValidator()
            double_validator.setRange(-1e10, 1e10, 2)
            editor.setValidator(double_validator)
            return editor

        else:
            return super().createEditor(parent, option, index)

    def sizeHint(self, option, index):
        if self.horizontal_header_data_is(index, ObjectiveColumnNames.direction):
            size = super().sizeHint(option, index)
            size.setWidth(24 + size.width())
            return size
        else:
            return super().sizeHint(option, index)

    def paint(self, painter, option, index):
        if self.horizontal_header_data_is(index, ObjectiveColumnNames.direction):
            cb = QtWidgets.QStyleOptionComboBox()
            # noinspection PyUnresolvedReferences
            cb.rect = option.rect
            cb.currentText = index.model().data(index, Qt.ItemDataRole.DisplayRole)
            QtWidgets.QApplication.style().drawComplexControl(QtWidgets.QStyle.ComplexControl.CC_ComboBox, cb, painter)
            QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.ControlElement.CE_ComboBoxLabel, cb, painter)

        else:
            super().paint(painter, option, index)

    def setEditorData(self, editor, index):
        if self.horizontal_header_data_is(index, ObjectiveColumnNames.direction):
            editor: QComboBox
            value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
            editor.setCurrentText(value)

        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if self.horizontal_header_data_is(index, ObjectiveColumnNames.direction):
            editor: QComboBox
            model.setData(index, editor.currentText(), Qt.ItemDataRole.DisplayRole)

        else:
            super().setModelData(editor, model, index)


class ObjectiveTableItemModel(StandardItemModelWithHeaderSearch):

    def __init__(self, parent=None, _with_dummy=True):
        super().__init__(parent)
        if _with_dummy or (__name__ == '__main__'):
            self.__set_dummy_data()

    def __set_dummy_data(self):
        rows = 3
        columns = len(ObjectiveColumnNames)

        with EditModel(self):
            self.setRowCount(rows + 1)  # header row for treeview
            self.setColumnCount(columns)

            # header
            for c, prop in enumerate(ObjectiveColumnNames):
                self.setHeaderData(
                    _section := c,
                    _orientation := Qt.Orientation.Horizontal,
                    _value := prop,
                    _role := Qt.ItemDataRole.DisplayRole
                )

                self.setHeaderData(
                    _section := c,
                    _orientation := Qt.Orientation.Horizontal,
                    _value := prop,
                    _role := Qt.ItemDataRole.UserRole,
                )

            # header row
            for c, prop in enumerate(ObjectiveColumnNames):
                item = QStandardItem()
                item.setText(prop)
                self.setItem(0, c, item)

            # table
            for r in range(1, rows+1):
                for c in range(columns):
                    item = QStandardItem()
                    # NOTE: The default implementation treats Qt::EditRole and Qt::DisplayRole as referring to the same data.
                    # item.setData(f'text{r}{c}', role=Qt.ItemDataRole.EditRole)
                    item.setData(f'text{r}{c}', role=Qt.ItemDataRole.DisplayRole)
                    item.setData(f'tooltip of {r}{c}', role=Qt.ItemDataRole.ToolTipRole)
                    item.setData(f'WhatsThis of {r}{c}', role=Qt.ItemDataRole.WhatsThisRole)
                    # item.setData(QSize(w=10, h=19), role=Qt.ItemDataRole.SizeHintRole)  # 悪い
                    item.setData(f'internal_text{r}{c}', role=Qt.ItemDataRole.UserRole)
                    # item.setText(f'text{r}{c}')

                    if c == 1 or c == 2:
                        icon = QIcon(ICON_PATH)  # Cannot read .ico file, but can .svg file?
                        item.setIcon(icon)

                    if c == 0 or c == 2:
                        item.setCheckable(True)
                        item.setCheckState(Qt.CheckState.Checked)

                    if c == 2:
                        # current_text = item.text()
                        current_text = item.data(Qt.ItemDataRole.DisplayRole)
                        item.setText(current_text + '\n2 line')

                    if c == 3:
                        item.setText(ObjectiveDirection.minimize)

                    self.setItem(r, c, item)

    def flags(self, index):

        r = index.row()

        # target_value 列は direction 列の値に基づいて Disable にする
        if horizontal_header_data_is(index, ObjectiveColumnNames.target_value):
            c = self.get_column_by_header_data(ObjectiveColumnNames.direction)
            if self.item(r, c).text() != ObjectiveDirection.specific_value:
                return super().flags(index) & ~Qt.ItemFlag.ItemIsEnabled

        return super().flags(index)

    def load_from_femtet(self):
        from pyfemtet_opt_gui_2.femtet.femtet import get_femtet, get_prm_result_names
        Femtet = get_femtet()
        names = get_prm_result_names(Femtet)

        rows = len(names)
        columns = len(ObjectiveColumnNames)

        with EditModel(self):
            self.setRowCount(rows + 1)  # header row for treeview
            self.setColumnCount(columns)

            # header
            for c, prop in enumerate(ObjectiveColumnNames):
                self.setHeaderData(
                    _section := c,
                    _orientation := Qt.Orientation.Horizontal,
                    _value := prop,
                    _role := Qt.ItemDataRole.DisplayRole
                )

                self.setHeaderData(
                    _section := c,
                    _orientation := Qt.Orientation.Horizontal,
                    _value := prop,
                    _role := Qt.ItemDataRole.UserRole,
                )

            # header row
            for c, prop in enumerate(ObjectiveColumnNames):
                item = QStandardItem()
                item.setText(prop)
                self.setItem(0, c, item)

            # table
            for r in range(1, rows + 1):
                for c in range(columns):
                    item = QStandardItem()


class ObjectiveItemModelWithoutHeader(StandardItemModelWithoutHeader):
    pass


class ObjectiveWizardPage(QWizardPage):

    ui: Ui_WizardPage_obj
    source_model: ObjectiveTableItemModel
    proxy_model: ObjectiveItemModelWithoutHeader
    delegate: ObjectiveItemDelegate

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_view()
        self.setup_model()
        self.setup_delegate()

    def setup_ui(self):
        self.ui = Ui_WizardPage_obj()
        self.ui.setupUi(self)

    def setup_view(self):
        self.ui.tableView_obj.clicked.connect(
            # self.ui.tableView_obj.edit
            lambda *args, **kwargs: start_edit_specific_column(
                self.ui.tableView_obj.edit,
                ObjectiveColumnNames.direction,
                *args,
                **kwargs
            )
        )

    def setup_model(self):
        self.source_model = get_obj_model()
        self.proxy_model = StandardItemModelWithoutHeader()
        self.proxy_model.setSourceModel(self.source_model)
        self.proxy_model.dataChanged.connect(lambda *args: resize_column(self.ui.tableView_obj, *args))
        self.ui.tableView_obj.setModel(self.proxy_model)
        self.resize_column()

    def setup_delegate(self):
        self.delegate = ObjectiveItemDelegate()
        self.ui.tableView_obj.setItemDelegate(self.delegate)
        self.resize_column()

    def resize_column(self):
        items = []
        for r in range(self.source_model.rowCount()):
            for c in range(self.source_model.columnCount()):
                items.append(self.source_model.item(r, c))
        resize_column(self.ui.tableView_obj, *items)


if __name__ == '__main__':
    app = QApplication()
    app.setStyle('fusion')

    page_obj = ObjectiveWizardPage()
    page_obj.show()

    sys.exit(app.exec())
