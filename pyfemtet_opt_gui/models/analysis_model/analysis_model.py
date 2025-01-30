import os
import enum
from contextlib import nullcontext

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

from pyfemtet_opt_gui.ui.ui_WizardPage_analysis_model import Ui_WizardPage

from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui.common.return_msg import *
from pyfemtet_opt_gui.common.expression_processor import *
from pyfemtet_opt_gui.common.titles import *
from pyfemtet_opt_gui.femtet.femtet import *

# ===== model =====
_FEMPRJ_MODEL = None
_FEMPRJ_MODEL_FOR_PROBLEM = None


def get_am_model(parent) -> 'FemprjModel':
    global _FEMPRJ_MODEL
    if _FEMPRJ_MODEL is None:
        _FEMPRJ_MODEL = FemprjModel(parent=parent, _with_dummy=False)
    return _FEMPRJ_MODEL


def get_am_model_for_problem(parent) -> 'FemprjModelForProblem':
    global _FEMPRJ_MODEL_FOR_PROBLEM
    if _FEMPRJ_MODEL_FOR_PROBLEM is None:
        _FEMPRJ_MODEL_FOR_PROBLEM = FemprjModelForProblem(parent)
        _FEMPRJ_MODEL_FOR_PROBLEM.setSourceModel(get_am_model(parent))
    return _FEMPRJ_MODEL_FOR_PROBLEM


# ===== warning dialog =====
_WARNED = False


# original model
class FemprjModel(StandardItemModelWithHeader):
    class RowNames(enum.StrEnum):
        femprj_path = 'プロジェクトファイルのパス'
        model_name = '解析モデル名'

    class ColumnNames(enum.StrEnum):
        item = '項目'
        value = '値'

    def __init__(self, parent=None, _with_dummy=True, with_first_row=True):
        super().__init__(parent, _with_dummy, with_first_row)
        self.setup_model()

    def setup_model(self):
        # set size
        with nullcontext():
            # row count
            n_rows = len(self.RowNames)
            if self.with_first_row:
                n_rows += 1
            self.setRowCount(n_rows)

            # column count
            n_cols = len(self.ColumnNames)
            self.setColumnCount(n_cols)

        # femprj
        with nullcontext():
            vhd = self.RowNames.femprj_path
            r = self.get_row_by_header_data(vhd)

            # item
            with nullcontext():
                c = self.get_column_by_header_data(self.ColumnNames.item)
                self.setItem(r, c, QStandardItem(vhd))

            # value
            with nullcontext():
                c = self.get_column_by_header_data(self.ColumnNames.value)
                item = QStandardItem()
                item.setData('ignore', CustomItemDataRole.CustomResizeRole)
                self.setItem(r, c, item)

        # model
        with nullcontext():
            vhd = self.RowNames.model_name
            r = self.get_row_by_header_data(vhd)

            # item
            with nullcontext():
                c = self.get_column_by_header_data(self.ColumnNames.item)
                self.setItem(r, c, QStandardItem(vhd))

            # value
            with nullcontext():
                c = self.get_column_by_header_data(self.ColumnNames.value)
                self.setItem(r, c, QStandardItem())

    def _set_dummy_data(self, n_rows=None):

        # set size
        with nullcontext():
            # row count
            n_rows = len(self.RowNames)
            if self.with_first_row:
                n_rows += 1
            self.setRowCount(n_rows)

            # column count
            n_cols = len(self.ColumnNames)
            self.setColumnCount(n_cols)

        # femprj
        with nullcontext():
            vhd = self.RowNames.femprj_path
            r = self.get_row_by_header_data(vhd)

            # item
            with nullcontext():
                c = self.get_column_by_header_data(self.ColumnNames.item)
                self.setItem(r, c, QStandardItem(vhd))

            # value
            with nullcontext():
                c = self.get_column_by_header_data(self.ColumnNames.value)
                item = QStandardItem('sample.femprj')
                item.setData('ignore', CustomItemDataRole.CustomResizeRole)
                self.setItem(r, c, item)

        # model
        with nullcontext():
            vhd = self.RowNames.model_name
            r = self.get_row_by_header_data(vhd)

            # item
            with nullcontext():
                c = self.get_column_by_header_data(self.ColumnNames.item)
                self.setItem(r, c, QStandardItem(vhd))

            # value
            with nullcontext():
                c = self.get_column_by_header_data(self.ColumnNames.value)
                self.setItem(r, c, QStandardItem('解析モデル'))

    def load_femtet(self) -> ReturnMsg:

        # 名前を取得
        names, ret_msg = get_name()

        # Femtet エラーならば何もしない
        if not can_continue(ret_msg, parent=self.parent()):
            return ret_msg

        # 名前を更新
        femprj_path, model_name = names

        # femprj_path
        with nullcontext():
            vhd = self.RowNames.femprj_path
            r = self.get_row_by_header_data(vhd)
            c = self.get_column_by_header_data(self.ColumnNames.value)
            self.item(r, c).setText(femprj_path)
            self.item(r, c).setToolTip(femprj_path)

        # model
        with nullcontext():
            vhd = self.RowNames.model_name
            r = self.get_row_by_header_data(vhd)
            c = self.get_column_by_header_data(self.ColumnNames.value)
            self.item(r, c).setText(model_name)

        return ReturnMsg.no_message

    def get_current_names(self):
        # femprj_path
        with nullcontext():
            vhd = self.RowNames.femprj_path
            r = self.get_row_by_header_data(vhd)
            c = self.get_column_by_header_data(self.ColumnNames.value)
            femprj_path = self.item(r, c).text()

        # model
        with nullcontext():
            vhd = self.RowNames.model_name
            r = self.get_row_by_header_data(vhd)
            c = self.get_column_by_header_data(self.ColumnNames.value)
            model_name = self.item(r, c).text()

        return femprj_path, model_name

    def is_valid(self):

        femprj_path, model_name = self.get_current_names()
        if not os.path.exists(femprj_path):
            return False

        # 名前を取得
        names, ret_msg = get_name()

        # Femtet エラーならば False
        if not can_continue(ret_msg, parent=self.parent()):
            return False

        # 万一名前が違えば False
        if os.path.abspath(names[0]).lower() != os.path.abspath(femprj_path).lower():
            return False

        # 万一名前が違えば False
        if names[1].lower() != model_name.lower():
            return False

        return True


# for problem view
class FemprjModelForProblem(ProxyModelWithForProblem):

    def filterAcceptsColumn(self, source_column, source_parent):
        return QSortFilterProxyModelOfStandardItemModel.filterAcceptsColumn(self, source_column, source_parent)

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex):
        return QSortFilterProxyModelOfStandardItemModel.filterAcceptsRow(self, source_row, source_parent)


# page
class AnalysisModelWizardPage(TitledWizardPage):
    ui: Ui_WizardPage
    source_model: FemprjModel
    proxy_model: StandardItemModelWithoutFirstRow
    column_resizer: ResizeColumn

    page_name = PageSubTitles.analysis_model

    def __init__(self, parent=None, load_femtet_fun=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_model()
        self.setup_view()
        self.setup_signal(load_femtet_fun)

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)

    def setup_model(self):
        self.source_model = get_am_model(parent=self)
        self.proxy_model = StandardItemModelWithoutFirstRow(parent=self)
        self.proxy_model.setSourceModel(self.source_model)

    def setup_view(self):
        view = self.ui.tableView
        view.setModel(self.proxy_model)

        self.column_resizer = ResizeColumn(view)
        self.column_resizer.resize_all_columns()

    def setup_signal(self, load_femtet_fun):
        # button を押したら状態を更新する
        self.ui.pushButton_load.clicked.connect(
            (lambda *_: self.source_model.load_femtet())
            if load_femtet_fun is None else
            (lambda *_: load_femtet_fun())
        )

        # 状態が変わったら isComplete を更新する
        self.source_model.dataChanged.connect(
            lambda *_: self.completeChanged.emit()
        )

    def isComplete(self) -> bool:
        return self.source_model.is_valid()

    def validatePage(self):
        """Next を押されたとき"""

        # 再度モデルを確認する
        self.completeChanged.emit()

        # モデルが valid
        if self.isComplete():
            return True

        # モデルが invalid
        else:
            ret_msg = ReturnMsg.Error.femprj_or_model_inconsistent
            can_continue(ret_msg, parent=self)
            return False


if __name__ == '__main__':
    # _WITH_DUMMY = True  # comment out to prevent debug
    # from pyfemtet_opt_gui.femtet.mock import get_femtet, get_obj_names  # comment out to prevent debug

    get_femtet()

    app = QApplication()
    app.setStyle('fusion')

    page_obj = AnalysisModelWizardPage()
    page_obj.show()

    app.exec()
