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

from pyfemtet_opt_gui_2.common.qt_util import *
from pyfemtet_opt_gui_2.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui_2.common.return_msg import ReturnMsg, show_return_msg
from pyfemtet_opt_gui_2.femtet.femtet import get_femtet, get_obj_names, open_help

ICON_PATH = r'pyfemtet-opt-gui\pyfemtet_opt_gui_2\assets\icon\arrow.svg'

# ===== model =====
OBJ_MODEL = None
_WITH_DUMMY = False


def get_obj_model() -> 'ObjectiveTableItemModel':
    global OBJ_MODEL
    if OBJ_MODEL is None:
        OBJ_MODEL = ObjectiveTableItemModel(_with_dummy=_WITH_DUMMY)
    return OBJ_MODEL


# ===== constants =====
class ObjectiveColumnNames(enum.StrEnum):
    use = CommonItemColumnName.use
    name = '名前'
    direction = '最適化の目標',
    target_value = '目標値',
    note = '備考',


class ObjectiveDirection(enum.StrEnum):  # python >= 3.11
    minimize = 'minimize'
    maximize = 'maximize'
    specific_value = 'aim for'


# ===== qt objects =====
class ObjectiveItemDelegate(QStyledItemDelegate):

    def create_combobox(self, parent, default_value=None):
        cb = QComboBox(parent)
        cb.addItems([p for p in ObjectiveDirection])
        if default_value is not None:
            cb.setCurrentText(default_value)  # 選択肢になければ無視される模様
        cb.setFrame(False)
        return cb

    def update_model(self, text, index):
        with EditModel(index.model()):
            index.model().setData(index, text, Qt.ItemDataRole.DisplayRole)

    def createEditor(self, parent, option, index):
        if get_internal_header_data(index) == ObjectiveColumnNames.direction:
            # combobox の作成
            cb = self.create_combobox(parent, default_value=index.model().data(index, Qt.ItemDataRole.DisplayRole))
            # combobox の選択を変更したらセルの値も変更して
            # combobox のあるセルに基づいて振る舞いが変わる
            # セルの振る舞いを即時変えるようにする
            cb.currentTextChanged.connect(lambda text: self.update_model(text, index))
            # combobox が作成されたら即時メニューを展開する
            QTimer.singleShot(0, cb.showPopup)
            return cb

        elif get_internal_header_data(index) == ObjectiveColumnNames.target_value:
            editor: QLineEdit = super().createEditor(parent, option, index)
            double_validator = QDoubleValidator()
            double_validator.setRange(-1e10, 1e10, 2)
            editor.setValidator(double_validator)
            return editor

        else:
            return super().createEditor(parent, option, index)

    def sizeHint(self, option, index):
        if get_internal_header_data(index) == ObjectiveColumnNames.direction:
            size = super().sizeHint(option, index)
            size.setWidth(24 + size.width())
            return size
        else:
            return super().sizeHint(option, index)

    def paint(self, painter, option, index):
        if get_internal_header_data(index) == ObjectiveColumnNames.direction:
            cb = QtWidgets.QStyleOptionComboBox()
            # noinspection PyUnresolvedReferences
            cb.rect = option.rect
            cb.currentText = index.model().data(index, Qt.ItemDataRole.DisplayRole)
            QtWidgets.QApplication.style().drawComplexControl(QtWidgets.QStyle.ComplexControl.CC_ComboBox, cb, painter)
            QtWidgets.QApplication.style().drawControl(QtWidgets.QStyle.ControlElement.CE_ComboBoxLabel, cb, painter)

        else:
            super().paint(painter, option, index)

    def setEditorData(self, editor, index):
        if get_internal_header_data(index) == ObjectiveColumnNames.direction:
            editor: QComboBox
            value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
            editor.setCurrentText(value)

        else:
            super().setEditorData(editor, index)

    def setModelData(self, editor, model, index):
        if get_internal_header_data(index) == ObjectiveColumnNames.direction:
            editor: QComboBox
            with EditModel(model):
                model.setData(index, editor.currentText(), Qt.ItemDataRole.DisplayRole)

        else:
            super().setModelData(editor, model, index)


class ObjectiveTableItemModel(StandardItemModelWithHeaderSearch):

    def __init__(self, parent=None, _with_dummy=True):
        super().__init__(parent)

        self.setup_header_data()
        if _with_dummy:
            self.__set_dummy_data()

    def setup_header_data(self):
        with EditModel(self):
            self.setColumnCount(len(ObjectiveColumnNames))
            for c, prop in enumerate(ObjectiveColumnNames):
                # headerData
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

            # first row == header row for treeview
            self.setRowCount(1)
            for c, prop in enumerate(ObjectiveColumnNames):
                item = QStandardItem()
                item.setText(prop)
                self.setItem(0, c, item)

    def __set_dummy_data(self):
        rows = 3
        columns = len(ObjectiveColumnNames)

        with EditModel(self):
            self.setRowCount(rows + 1)  # header row for treeview

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
        if get_internal_header_data(index) == ObjectiveColumnNames.target_value:
            c = self.get_column_by_header_data(ObjectiveColumnNames.direction)
            if self.item(r, c).text() != ObjectiveDirection.specific_value:
                return super().flags(index) & ~Qt.ItemFlag.ItemIsEnabled

        return super().flags(index)

    def load_from_femtet(self):
        obj_names, ret_msg = get_obj_names()

        if ret_msg != ReturnMsg.no_message:
            show_return_msg(ret_msg)

        rows = len(obj_names)

        with EditModel(self):
            self.setRowCount(rows + 1)  # header row for treeview

            # table
            for r, obj_name in zip(range(1, rows + 1), obj_names):

                c = self.get_column_by_header_data(ObjectiveColumnNames.use)
                item = QStandardItem()
                item.setCheckable(True)
                item.setCheckState(Qt.CheckState.Checked)
                item.setEditable(False)
                self.setItem(r, c, item)

                c = self.get_column_by_header_data(ObjectiveColumnNames.name)
                item = QStandardItem()
                item.setText(obj_name)
                item.setEditable(False)
                self.setItem(r, c, item)

                c = self.get_column_by_header_data(ObjectiveColumnNames.direction)
                item = QStandardItem()
                item.setText(ObjectiveDirection.minimize)
                self.setItem(r, c, item)

                c = self.get_column_by_header_data(ObjectiveColumnNames.target_value)
                item = QStandardItem()
                item.setText('0')
                self.setItem(r, c, item)


class ObjectiveItemModelWithoutFirstRow(StandardItemModelWithoutFirstRow):
    pass


class ObjectiveWizardPage(QWizardPage):

    ui: Ui_WizardPage_obj
    source_model: ObjectiveTableItemModel
    proxy_model: ObjectiveItemModelWithoutFirstRow
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
        self.ui.commandLinkButton.clicked.connect(
            lambda *args: open_help('ParametricAnalysis/ParametricAnalysis.htm')
        )

    def setup_view(self):

        view = self.ui.tableView

        # direction 列のみシングルクリックでコンボボックスが
        # 開くようにシングルクリックで edit モードに入るよう
        # にする
        view.clicked.connect(
            lambda *args, **kwargs: start_edit_specific_column(
                self.ui.tableView.edit,
                ObjectiveColumnNames.direction,
                *args,
                **kwargs
            )
        )

    def setup_model(self):
        self.source_model = get_obj_model()
        self.proxy_model = StandardItemModelWithoutFirstRow()
        self.proxy_model.setSourceModel(self.source_model)
        self.proxy_model.dataChanged.connect(
            lambda *args: resize_column(self.ui.tableView, *args)
        )
        self.ui.tableView.setModel(self.proxy_model)
        self.resize_column()
        self.ui.pushButton.clicked.connect(self.source_model.load_from_femtet)

    def setup_delegate(self):
        self.delegate = ObjectiveItemDelegate()
        self.ui.tableView.setItemDelegate(self.delegate)
        self.resize_column()

    def resize_column(self):
        items = []
        for r in range(self.source_model.rowCount()):
            for c in range(self.source_model.columnCount()):
                items.append(self.source_model.item(r, c))
        resize_column(self.ui.tableView, *items)


if __name__ == '__main__':
    _WITH_DUMMY = True  # comment out to prevent debug
    from pyfemtet_opt_gui_2.femtet.mock import get_femtet, get_obj_names  # comment out to prevent debug

    get_femtet()

    app = QApplication()
    app.setStyle('fusion')

    page_obj = ObjectiveWizardPage()
    page_obj.show()

    sys.exit(app.exec())
