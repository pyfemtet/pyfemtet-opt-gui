import os
import sys

from PySide6.QtWidgets import (QApplication, QWizard, QFileDialog)

from ui.ui_wizard import Ui_Wizard
from problem_model import ProblemItemModel, CustomProxyModel
from obj_model import ObjTableDelegate
from script_builder import build_script

from pyfemtet_opt_gui.ui.return_code import ReturnCode

import _p  # must be same folder and cannot import via `from` keyword.


# noinspection PyMethodMayBeStatic
class MainWizard(QWizard):

    def __init__(self, problem: ProblemItemModel, parent=None):
        super().__init__(parent=parent)
        self._problem: ProblemItemModel = problem

    def set_ui(self, ui):
        # noinspection PyAttributeOutsideInit
        self._ui = ui

        # set optimization settings
        model = self._problem.run_model
        self._ui.tableView_run.setModel(model)

    def update_problem(self):
        ret_code = self.load_femprj()
        if ret_code in ReturnCode.WARNING:
            _p.logger.warning(ret_code.value)
        elif ret_code in ReturnCode.ERROR:
            _p.logger.error(ret_code.value)
            return

        if self._ui.plainTextEdit_prj.toPlainText():
            ret_code = self.load_prm()
            if ret_code in ReturnCode.WARNING:
                _p.logger.warning(ret_code.value)
            elif ret_code in ReturnCode.ERROR:
                _p.logger.error(ret_code.value)
                return

            ret_code = self.load_obj()
            if ret_code in ReturnCode.WARNING:
                _p.logger.warning(ret_code.value)
            elif ret_code in ReturnCode.ERROR:
                _p.logger.error(ret_code.value)
                return

    def load_femprj(self) -> ReturnCode:
        # モデルの再読み込み
        ret_code = self._problem.femprj_model.load()
        prj, model = self._problem.femprj_model.get_femprj()
        self._ui.plainTextEdit_prj.setPlainText(prj)
        self._ui.plainTextEdit_model.setPlainText(model)
        return ret_code

    def load_prm(self) -> ReturnCode:
        if self._ui.plainTextEdit_prj.toPlainText():
            # モデルの再読み込み
            ret_code = self._problem.prm_model.load()
            # モデルをビューに再設定
            model = self._problem.prm_model
            self._ui.tableView_prm.setModel(model)
            return ret_code

        else:
            return ReturnCode.WARNING.PARAMETER_EMPTY

    def load_obj(self) -> ReturnCode:
        if self._ui.plainTextEdit_prj.toPlainText():
            # モデルの再読み込み
            ret_code = self._problem.obj_model.load()

            # モデルをビューに再設定
            model = self._problem.obj_model
            self._ui.tableView_obj.setModel(model)
            delegate = ObjTableDelegate(model)
            self._ui.tableView_obj.setItemDelegate(delegate)
            return ret_code

        else:
            return ReturnCode.WARNING.PARAMETRIC_OUTPUT_EMPTY

    def connect_process(self):
        if _p.connect_femtet():
            _p.logger.info(f'Connected! (pid: {_p.pid})')  # TODO: show dialog

            # update model
            self.update_problem()

    def build_script(self):

        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("Python files (*.py)")

        if dialog.exec():
            path = dialog.selectedFiles()[0]
            dir_path = os.path.dirname(path)
            if os.path.isdir(dir_path):
                build_script(self._problem, path)
            else:
                _p.logger.error('存在しないフォルダのファイルが指定されました。')


if __name__ == '__main__':

    app = QApplication(sys.argv)

    g_problem: ProblemItemModel = ProblemItemModel()

    wizard = MainWizard(g_problem)

    ui_wizard = Ui_Wizard()
    ui_wizard.setupUi(wizard)

    proxy_model = CustomProxyModel(g_problem)
    proxy_model.setSourceModel(g_problem)
    ui_wizard.treeView.setModel(proxy_model)

    wizard.set_ui(ui_wizard)  # ui を登録
    wizard.update_problem()  # ui へのモデルの登録

    wizard.show()  # ビューの表示
    sys.exit(app.exec())  # アプリケーションの実行
