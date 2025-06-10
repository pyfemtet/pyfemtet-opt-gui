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
from contextlib import nullcontext

from pyfemtet_opt_gui.ui.ui_WizardPage_obj import Ui_WizardPage_obj

from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui.common.return_msg import *
from pyfemtet_opt_gui.common.titles import *
import pyfemtet_opt_gui.fem_interfaces as fi

# ===== model =====
OBJ_MODEL = None


def get_obj_model(parent=None, _dummy_data=None) -> 'ObjectiveTableItemModel':
    global OBJ_MODEL
    if OBJ_MODEL is None:
        OBJ_MODEL = ObjectiveTableItemModel(
            parent=parent,
            _dummy_data=(
                _default_dummy_data if _dummy_data is True
                else _dummy_data
            ),
        )
    return OBJ_MODEL


def get_obj_model_for_problem(parent, _dummy_data=None):
    model = get_obj_model(parent, _dummy_data)
    model_for_problem = QObjectiveItemModelForProblemTableView(parent)
    model_for_problem.setSourceModel(model)
    return model_for_problem


def _reset_obj_model():
    global OBJ_MODEL
    OBJ_MODEL = None


# ===== constants =====
class ObjectiveColumnNames(enum.StrEnum):
    use = CommonItemColumnName.use
    name = '名前'
    direction = '最適化の目標'
    target_value = '目標値'
    note = 'メモ欄'


class ObjectiveDirection(enum.StrEnum):  # python >= 3.11
    minimize = 'minimize'
    maximize = 'maximize'
    specific_value = 'aim for'


_default_dummy_data = {
    ObjectiveColumnNames.use: [True, True, True],
    ObjectiveColumnNames.name: ['obj1', 'obj2', 'obj3'],
    ObjectiveColumnNames.direction: [ObjectiveDirection.maximize, ObjectiveDirection.minimize, ObjectiveDirection.specific_value],
    ObjectiveColumnNames.target_value: [None, None, 10.],
    ObjectiveColumnNames.note: [None, None, None],
}


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
            editor = super().createEditor(parent, option, index)
            assert isinstance(editor, QLineEdit)
            double_validator = QDoubleValidator()
            double_validator.setRange(-1e20, 1e20, 2)
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


class ObjectiveTableItemModel(StandardItemModelWithHeader):
    ColumnNames = ObjectiveColumnNames

    def _set_dummy_data(self, _dummy_data: dict):

        rows = 1 + len(tuple(_dummy_data.values())[0])
        columns = len(self.ColumnNames)
        self.setRowCount(rows)
        self.setColumnCount(columns)

        iterable = self.get_row_iterable()
        for key, values in _dummy_data.items():
            for i, (r, value) in enumerate(zip(iterable, values)):

                c = self.get_column_by_header_data(key)
                item = QStandardItem()

                # self.ColumnNames.use
                if key == self.ColumnNames.use:
                    item.setCheckable(True)
                    item.setCheckState(Qt.CheckState.Checked)
                    item.setEditable(False)

                # self.ColumnNames.name
                elif key == self.ColumnNames.name:
                    item.setText(str(value))
                    item.setEditable(False)

                # self.ColumnNames.direction
                elif key == self.ColumnNames.direction:
                    item.setText(str(value))

                # self.ColumnNames.direction
                elif key == self.ColumnNames.target_value:
                    if value is None:
                        item.setText('0')
                    else:
                        item.setText(str(value))

                elif key == self.ColumnNames.note:
                    if value is not None:
                        item.setText(str(value))

                else:
                    raise Exception(f'ダミーデータが不正, {key}')

                self.setItem(r, c, item)

    def flags(self, index):

        r = index.row()

        # target_value 列は direction 列の値に基づいて Disable にする
        if get_internal_header_data(index) == ObjectiveColumnNames.target_value:
            c = self.get_column_by_header_data(ObjectiveColumnNames.direction)
            if self.item(r, c).text() != ObjectiveDirection.specific_value:
                return super().flags(index) & ~Qt.ItemFlag.ItemIsEnabled

        return super().flags(index)

    def load_femtet(self) -> ReturnMsg:
        # parametric if 設定取得
        obj_names, ret_msg = fi.get().get_obj_names()
        if not can_continue(ret_msg, parent=self.parent()):
            return ret_msg

        # 現在の状態を stash
        stashed_data: dict[str, dict[str, dict[Qt.ItemDataRole, ...]]] = self.stash_current_table()

        rows = len(obj_names) + 1
        with EditModel(self):
            self.setRowCount(rows)  # header row for treeview

            for r, name in zip(range(1, rows), obj_names):

                # ===== use =====
                with nullcontext():
                    item = QStandardItem()
                    item.setCheckable(True)
                    item.setEditable(False)

                    # stashed data の中に obj_name があればそれを復元
                    if name in stashed_data.keys():
                        self.set_data_from_stash(
                            item, name, self.ColumnNames.use, stashed_data
                        )

                    # デフォルトは True
                    else:
                        item.setCheckState(Qt.CheckState.Checked)

                    # item を作成
                    c = self.get_column_by_header_data(self.ColumnNames.use)
                    self.setItem(r, c, item)

                # ===== name =====
                with nullcontext():
                    # これは stash を復元する必要がない
                    item = QStandardItem()
                    item.setText(name)
                    item.setEditable(False)
                    c = self.get_column_by_header_data(self.ColumnNames.name)
                    self.setItem(r, c, item)

                # ===== direction =====
                with nullcontext():
                    item = QStandardItem()

                    # stashed data の中に obj_name があればそれを復元
                    if name in stashed_data.keys():
                        self.set_data_from_stash(
                            item, name, self.ColumnNames.direction, stashed_data
                        )

                    # デフォルトは minimize
                    else:
                        value = ObjectiveDirection.minimize
                        item.setText(value)

                    c = self.get_column_by_header_data(self.ColumnNames.direction)
                    self.setItem(r, c, item)

                # ===== target_value =====
                with nullcontext():
                    item = QStandardItem()

                    # stashed data の中に obj_name があればそれを復元
                    if name in stashed_data.keys():
                        self.set_data_from_stash(
                            item, name, self.ColumnNames.target_value, stashed_data
                        )

                    # デフォルトは 0
                    else:
                        item.setText('0')

                    c = self.get_column_by_header_data(self.ColumnNames.target_value)
                    self.setItem(r, c, item)

                # ===== note =====
                with nullcontext():
                    item = QStandardItem()

                    # stashed data の中に obj_name があればそれを復元
                    if name in stashed_data.keys():
                        self.set_data_from_stash(
                            item, name, self.ColumnNames.note, stashed_data
                        )

                    # デフォルトは空欄
                    else:
                        item.setText('')

                    # item 作成
                    c = self.get_column_by_header_data(self.ColumnNames.note)
                    self.setItem(r, c, item)

        return ReturnMsg.no_message

    def is_nothing_checked(self) -> bool:
        # ひとつも used がなければ False
        hd = self.ColumnNames.use
        c = self.get_column_by_header_data(hd)
        check_list = []
        for r in self.get_row_iterable():
            check_list.append(self.item(r, c).checkState())
        # Checked がひとつもない
        return all([ch != Qt.CheckState.Checked for ch in check_list])

    def output_dict(self):
        # これは FemtetInterface の parametric_indexes_... 引数
        # だけを返す

        parametric_output_indexes_use_as_objective = dict()

        # use 列の列番号
        c_use = self.get_column_by_header_data(self.ColumnNames.use)

        # direction 列の列番号
        c_direction = self.get_column_by_header_data(self.ColumnNames.direction)

        # target_value 列の列番号
        c_target_value = self.get_column_by_header_data(self.ColumnNames.target_value)

        for parametric_output_index, r in enumerate(self.get_row_iterable()):

            # 使用していなければ次へ
            if self.item(r, c_use).checkState() != Qt.CheckState.Checked:
                continue

            # direction を取得
            direction = self.item(r, c_direction).text()

            # direction が aim to なら
            if direction == ObjectiveDirection.specific_value:

                # target_value を取得
                # delegate で doubleValidator の実装を
                # 維持している限り float にできる
                target = float(self.item(r, c_target_value).text())

                # index に対して target 値を入れる
                parametric_output_indexes_use_as_objective.update(
                    {parametric_output_index: target}
                )

            # そうでなければ
            else:

                # index に対して minimize 又は maximize を入れる
                parametric_output_indexes_use_as_objective.update(
                    {parametric_output_index: f'"{direction}"'}
                )

        return parametric_output_indexes_use_as_objective


class QObjectiveItemModelForProblemTableView(ProxyModelWithForProblem):

    def filterAcceptsColumn(self, source_column: int, source_parent: QModelIndex):
        # use を非表示
        source_model = self.sourceModel()
        assert isinstance(source_model, ObjectiveTableItemModel)
        if source_column == get_column_by_header_data(
                source_model,
                ObjectiveTableItemModel.ColumnNames.use
        ):
            return False

        return True


class ObjectiveItemModelWithoutFirstRow(StandardItemModelWithoutFirstRow):
    pass


class ObjectiveWizardPage(TitledWizardPage):
    ui: Ui_WizardPage_obj
    source_model: ObjectiveTableItemModel
    proxy_model: ObjectiveItemModelWithoutFirstRow
    delegate: ObjectiveItemDelegate
    column_resizer: ResizeColumn

    page_name = PageSubTitles.obj

    def __init__(
            self,
            parent=None,
            load_femtet_fun: callable = None,
            _dummy_data=None,
    ):
        super().__init__(parent, _dummy_data)
        self.setup_ui()
        self.setup_model(load_femtet_fun)
        self.setup_view()
        self.setup_delegate()

    def setup_ui(self):
        self.ui = Ui_WizardPage_obj()
        self.ui.setupUi(self)
        self.ui.commandLinkButton.clicked.connect(
            lambda *args: fi.get().open_help('ParametricAnalysis/ParametricAnalysis.htm')
        )

    def setup_model(self, load_femtet_fun):
        self.source_model = get_obj_model(self, _dummy_data=self._dummy_data)
        self.proxy_model = ObjectiveItemModelWithoutFirstRow(self)
        self.proxy_model.setSourceModel(self.source_model)

        # ボタンを押したらモデルを更新する
        self.ui.pushButton.clicked.connect(
            (lambda *args: self.source_model.load_femtet())
            if load_femtet_fun is None else
            (lambda *_: load_femtet_fun())
        )

        # ボタンを押したら checkState に関係なく
        # isComplete を更新する
        self.ui.pushButton.clicked.connect(
            lambda *args, **kwargs: self.completeChanged.emit()
        )

        # model の checkState が変更されたら
        # isComplete を更新する
        def filter_role(_1, _2, roles):
            if Qt.ItemDataRole.CheckStateRole in roles:  # or len(roles) == 0

                # 警告を表示する（編集は受け入れる）
                if self.source_model.is_nothing_checked():
                    ret_msg = ReturnMsg.Warn.no_objs_selected
                    show_return_msg(return_msg=ret_msg, parent=self)

                self.completeChanged.emit()

        self.source_model.dataChanged.connect(filter_role)

    def setup_view(self):

        view = self.ui.tableView

        # view に model を設定
        view.setModel(self.proxy_model)

        # 表示データが変わったときに列幅を自動調整
        # する設定
        self.column_resizer = ResizeColumn(view)

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

        # 一旦列幅を自動調整
        self.resize_column()

    def setup_delegate(self):
        self.delegate = ObjectiveItemDelegate()
        self.ui.tableView.setItemDelegate(self.delegate)
        self.resize_column()

    def resize_column(self):
        self.column_resizer.resize_all_columns()

    def isComplete(self) -> bool:
        if self.source_model.is_nothing_checked():
            return False
        else:
            return True


if __name__ == '__main__':
    # from pyfemtet_opt_gui.femtet.mock import get_femtet, get_obj_names  # comment out to prevent debug

    # fi.get().get_femtet()

    app = QApplication()
    app.setStyle('fusion')

    page_obj = ObjectiveWizardPage(_dummy_data=True)
    page_obj.show()

    sys.exit(app.exec())
