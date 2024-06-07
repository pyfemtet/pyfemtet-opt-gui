import sys

from PySide6.QtWidgets import (QApplication, QWizard)

from sandbox3.ui.ui_wizard import Ui_Wizard
from sandbox3.problem_model import ProblemItemModel, CustomProxyModel
from sandbox3.obj_model import ObjTableDelegate

import _p  # must be same folder and cannot import via `from` keyword.


# noinspection PyMethodMayBeStatic
class MainWizard(QWizard):

    def __init__(self, problem: ProblemItemModel, parent=None):
        super().__init__(parent=parent)
        self._problem: ProblemItemModel = problem

    def set_ui(self, ui):
        # noinspection PyAttributeOutsideInit
        self._ui = ui

    def load_prm(self):
        if self._ui.plainTextEdit_prj.toPlainText():
            # モデルの再読み込み
            self._problem.prm_model.load()
            # モデルをビューに再設定
            model = self._problem.prm_model
            self._ui.tableView_prm.setModel(model)

    def load_obj(self):
        if self._ui.plainTextEdit_prj.toPlainText():
            # モデルの再読み込み
            self._problem.obj_model.load()
            # モデルをビューに再設定
            model = self._problem.obj_model
            self._ui.tableView_obj.setModel(model)
            delegate = ObjTableDelegate(model)
            self._ui.tableView_obj.setItemDelegate(delegate)

    def load_model(self):
        if _p.check_femtet_alive():
            prj = _p.Femtet.Project
            model = _p.Femtet.AnalysisModelName
            if prj:
                self._ui.plainTextEdit_prj.setPlainText(prj)
                self._ui.plainTextEdit_model.setPlainText(model)
            else:
                _p.logger.warning('Femtet で解析プロジェクトが開かれていません。')
        else:
            _p.logger.warning('Femtet との接続ができていません。')

    def connect_process(self):
        if _p.connect_femtet():
            _p.logger.info(f'Connected! (pid: {_p.pid})')  # TODO: show dialog

            # update model
            self.update_model_via_ui()

    def update_model_via_ui(self):
        self.load_model()
        if self._ui.plainTextEdit_prj.toPlainText():
            self.load_prm()
            self.load_obj()


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
    wizard.update_model_via_ui()  # ui へのモデルの登録

    wizard.show()  # ビューの表示
    sys.exit(app.exec())  # アプリケーションの実行
