import os
import sys
from functools import partial

from PySide6.QtWidgets import (QApplication, QWizard, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QThread, Signal

from pyfemtet_opt_gui.ui.ui_detailed_wizard import Ui_DetailedWizard

from pyfemtet_opt_gui.item_as_model import MyStandardItemAsTableModelWithoutHeader
from pyfemtet_opt_gui.problem_model import ProblemItemModel, CustomProxyModel
from pyfemtet_opt_gui.obj_model import ObjTableDelegate

from pyfemtet_opt_gui.script_builder import build_script_main

from pyfemtet_opt_gui.ui.return_code import ReturnCode, should_stop

from pyfemtet_opt_gui.prm_model import PrmModel

import pyfemtet_opt_gui._p as _p  # must be same folder and cannot import via `from` keyword.

here = os.path.dirname(__file__)


# noinspection PyMethodMayBeStatic
class MainWizard(QWizard):

    def __init__(self, problem: ProblemItemModel, parent=None):
        super().__init__(parent=parent)
        self._problem: ProblemItemModel = problem
        self.worker = OptimizationWorker()
        self.worker.finished.connect(self.optimization_finished)
        self._ui: Ui_DetailedWizard = None

    def set_ui(self, ui):
        self._ui = ui

        # set optimization settings
        model = self._problem.run_model
        proxy_model = MyStandardItemAsTableModelWithoutHeader(model)
        proxy_model.setSourceModel(model)
        self._ui.tableView_run.setModel(proxy_model)

        # disable next button if checker returns False
        self._ui.wizardPage1_launch.isComplete = self.check_femtet_alive
        self._ui.wizardPage2_model.isComplete = partial(self.check_femprj_valid, show_warning=False)
        self._ui.wizardPage3_param.isComplete = partial(self.check_prm_used_any, show_warning=False)
        # self._ui.wizardPage4_cns.isComplete =  # constraint is not necessary.
        self._ui.wizardPage5_obj.isComplete = partial(self.check_obj_used_any, show_warning=False)
        # self._ui.wizardPage6_run.isComplete =  # currently, FEMOpt.optimize() requires no arguments.

        # connect dataChanged to completeChanged(=emit isComplete)
        for page_id in self.pageIds():
            page = self.page(page_id)
            self._problem.dataChanged.connect(page.completeChanged)

        # show warning if finish during optimization
        def validate_finish() -> bool:
            out = True
            if self.worker.running:
                ret = QMessageBox.warning(
                    self, 'warning', '最適化の実行中にダイアログを閉じると最適化は強制終了されます。よろしいですか？',
                    QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No
                )
                out = ret == QMessageBox.StandardButton.Yes
            return out
        self._ui.wizardPage9_verify.validatePage = validate_finish

        # running condition warning
        def validate_run_model() -> bool:
            out = True
            # If finish condition is not specified,
            # the optimization process will be an endless loop.
            if len(self._problem.run_model.get_finish_conditions()) == 0:
                ret = QMessageBox.warning(
                    self, 'warning', '終了判定に関わる条件が指定されていないため、生成されるプログラムは手動で停止するまで計算を続けます。よろしいですか？',
                    QMessageBox.StandardButton.Yes, QMessageBox.StandardButton.No
                )
                out = ret == QMessageBox.StandardButton.Yes
            return out
        self._ui.wizardPage6_run.validatePage = validate_run_model

    def update_problem(self, _=False, show_warning=True):  # _ is the disposal variable of click() signal.
        return_codes = list()

        return_codes.append(self.load_femprj())
        return_codes.append(self.load_prm())
        return_codes.append(self.load_obj())
        return_codes.append(self.load_cns())

        if show_warning:
            for return_code in return_codes:
                if should_stop(return_code):  # show message
                    break  # if error, stop show message

    def connect_process(self):
        button = self._ui.pushButton_launch

        button.setText('接続中です...')
        button.setEnabled(False)
        button.repaint()

        # If femtet is already connected or not
        if _p.check_femtet_alive():
            # already connected
            _p.logger.info(f'Femtet との接続はすでに確立しています。')

        else:
            # not connected
            if len(_p._get_pids('Femtet.exe')) == 0:
                # no Femtet exist
                button.setText('Femtet を起動して接続します。\n少し時間がかかります...')
            else:
                # Femtet exists
                button.setText('Femtet プロセスが見つかりました。\n接続しています...')
            button.repaint()

            # try to connect
            if _p.connect_femtet():
                # successfully connected to femtet
                _p.logger.info(f'Connected! (pid: {_p.pid})')  # TODO: show dialog
                # update model
                self.update_problem(show_warning=False)

            else:
                # failed to connect
                _p.logger.warning('Femtet との接続に失敗しました。')

        # open sample file if needed and femtet is connected
        if self._ui.checkBox_openSampleFemprj.isChecked() and _p.check_femtet_alive():
            femprj_path = os.path.join(here, 'test', 'test_parametric.femprj')
            _p.Femtet.LoadProject(
                femprj_path,
                True
            )
            self.update_problem(show_warning=False)

        # finalize
        button.setText(button.accessibleName())
        button.setEnabled(True)
        button.repaint()

        self._ui.wizardPage1_launch.completeChanged.emit()

    def load_femprj(self) -> ReturnCode:
        # モデルの再読み込み
        ret_code = self._problem.femprj_model.load()
        prj, model = self._problem.femprj_model.get_femprj()
        self._ui.plainTextEdit_prj.setPlainText(prj)
        self._ui.plainTextEdit_model.setPlainText(model)
        return ret_code

    def load_prm(self) -> ReturnCode:
        # モデルの再読み込み
        ret_code = self._problem.prm_model.load()

        # モデルをビューに再設定
        model = self._problem.prm_model
        proxy_model = MyStandardItemAsTableModelWithoutHeader(model)
        proxy_model.setSourceModel(model)
        self._ui.tableView_prm.setModel(proxy_model)

        return ret_code

    def load_obj(self) -> ReturnCode:
        # モデルの再読み込み
        ret_code = self._problem.obj_model.load()
        # モデルをビューに再設定
        model = self._problem.obj_model
        proxy_model = MyStandardItemAsTableModelWithoutHeader(model)
        proxy_model.setSourceModel(model)
        self._ui.tableView_obj.setModel(proxy_model)
        delegate = ObjTableDelegate(proxy_model)
        self._ui.tableView_obj.setItemDelegate(delegate)
        return ret_code

    def load_cns(self) -> ReturnCode:

        # モデルの再読み込み
        ret_code = self._problem.cns_model.load()

        # モデルをビューに再設定
        model = self._problem.cns_model
        proxy_model = MyStandardItemAsTableModelWithoutHeader(model)
        proxy_model.setSourceModel(model)
        self._ui.tableView_cnsList.setModel(proxy_model)
        return ret_code

    def build_script(self):

        # スクリプトの保存ファイル名を指定するダイアログ
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.FileMode.AnyFile)
        dialog.setNameFilter("Python files (*.py)")

        # ダイアログを表示
        if dialog.exec():
            # OK の場合
            path = dialog.selectedFiles()[0]

            # 拡張子を確認
            if not path.endswith('.py'):
                path += '.py'

            # ディレクトリの存在を確認
            dir_path = os.path.dirname(path)
            if not os.path.isdir(dir_path):
                _p.logger.error('存在しないフォルダのファイルが指定されました。')
                should_stop(ReturnCode.ERROR.DIRECTORY_NOT_EXISTS)
                return None

            # ファイル名が python モジュールとして正しいか確認
            file_name = os.path.basename(os.path.splitext(path)[0])
            # 英数字又は_以外を含む
            for char in file_name:
                if char not in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
                    should_stop(ReturnCode.ERROR.NOT_AS_PYTHON_MODULE)
                    return None
            # 数字で始まる
            if file_name[0] in '0123456789':
                should_stop(ReturnCode.ERROR.NOT_AS_PYTHON_MODULE)
                return None

            # 保存と実行
            with_run = self._ui.checkBox_save_with_run.checkState() == Qt.CheckState.Checked
            if with_run:
                self.worker.set(path, self._problem)
                self.start_optimization()
            else:
                build_script_main(self._problem, path, False)

    def check_femtet_alive(self):
        alive = _p.check_femtet_alive()

        label = self._ui.label_connectionState
        if alive:
            message = '接続されています。「次へ / Next」を押して下さい。'
            color = '009900'
        else:
            message = '接続されていません。'
            color = 'FF0000'

        text = f"<html><head/><body><p><span style='color:#{color}'>{message}</span></p></body></html>"
        label.setText(text)

        return alive

    def check_save_button_should_enabled(self):
        button = self._ui.pushButton_save_script
        if self.worker.running and self._ui.checkBox_save_with_run.isChecked():
            button.setEnabled(False)  # Disable the button while the function is running
            button.setText('最適化の実行中はスクリプトを保存できません。')
        else:
            button.setEnabled(True)  # Enable the button when the function has finished
            button.setText(button.accessibleName())

    def start_optimization(self):
        self.worker.start()
        self.worker.running = True  # おそらく実行時間の問題で self.run() が走るより先に check が走るので、先に True にしておく。
        self.check_save_button_should_enabled()

    def optimization_finished(self):
        self.check_save_button_should_enabled()

    def check_femprj_valid(self, show_warning=True):
        femprj_model = self._problem.femprj_model
        femprj, model = femprj_model.get_femprj()
        out = False
        if femprj == '':
            out = False
        elif not os.path.exists(femprj):
            out = False
        else:
            out = True
        if show_warning and not out:
            should_stop(ReturnCode.ERROR.FEMTET_NO_PROJECT, parent=self)
        return out

    def check_prm_used_any(self, show_warning=True):
        prm_model: 'PrmModel' = self._problem.prm_model
        col = prm_model.get_col_from_name(prm_model.USE)
        used = []
        for row in range(1, prm_model.rowCount()):
            index = prm_model.createIndex(row, col)
            used.append(prm_model.data(index, Qt.ItemDataRole.CheckStateRole))
        out = any(used)
        if show_warning and not out:
            should_stop(ReturnCode.WARNING.PARAMETER_NOT_SELECTED, parent=self)
        return out

    def check_obj_used_any(self, show_warning=True):
        obj_model = self._problem.obj_model
        col = obj_model.get_col_from_name('use')
        used = []
        for row in range(1, obj_model.rowCount()):
            index = obj_model.createIndex(row, col)
            used.append(obj_model.data(index, Qt.ItemDataRole.CheckStateRole))
        out = any(used)
        if show_warning and not out:
            should_stop(ReturnCode.WARNING.OBJECTIVE_NOT_SELECTED, parent=self)
        return out

    def update_analysis_model(self):
        button = self._ui.pushButton_test_prm
        prm_model: 'PrmModel' = self._problem.prm_model

        # disable button anyway
        button.setEnabled(False)
        button.repaint()

        # get used parameters
        params: dict = {}
        use_col = prm_model.get_col_from_name(prm_model.USE)
        name_col = prm_model.get_col_from_name(prm_model.NAME)
        test_col = prm_model.get_col_from_name(prm_model.TEST)
        for row in range(1, prm_model.rowCount()):
            use_index = prm_model.createIndex(row, use_col)
            if prm_model.data(use_index, Qt.ItemDataRole.CheckStateRole):
                name = prm_model.get_item(row, name_col).text()
                test_val = float(prm_model.get_item(row, test_col).text())
                params.update({name: test_val})

        # update Femtet's parameter
        try:
            for name, value in params.items():
                _p.Femtet.UpdateVariable(name, value)
            _p.Femtet.Gaudi.Activate()
            if not _p.Femtet.Gaudi.ReExecute(): raise Exception
            _p.Femtet.Redraw()
        except Exception as e:
            _p.logger.error(f'Femtet でのモデル再構築に失敗しました。エラーメッセージ:{e}')
            try:
                _p.Femtet.ShowLastError()
            except Exception as e:
                from traceback import print_exception
                print_exception(e)
            should_stop(ReturnCode.ERROR.FEMTET_RECONSTRUCT_FAILED, parent=self)

        # re-enable button anyway
        button.setEnabled(True)
        button.repaint()

    def show_cns_dialog(self):
        from pyfemtet_opt_gui.cns_dialog import ConstraintInputDialog
        dialog = ConstraintInputDialog(
            parent=self,
            f=Qt.WindowType.Dialog
        )
        dialog.show()

    def show_cns_dialog_edit(self):
        selected_proxy_cns_indexes = self._ui.tableView_cnsList.selectedIndexes()
        if not selected_proxy_cns_indexes:
            return

        # get source index
        proxy_model: MyStandardItemAsTableModelWithoutHeader = self._ui.tableView_cnsList.model()
        target_index = proxy_model.mapToSource(selected_proxy_cns_indexes[0])

        # get row
        row = target_index.row()

        # show editor
        from pyfemtet_opt_gui.cns_dialog import ConstraintInputDialog
        dialog = ConstraintInputDialog(
            parent=self,
            f=Qt.WindowType.Dialog,
            target_cns_row=row,
        )
        dialog.show()

    def remove_cns(self):
        selected_proxy_cns_indexes = self._ui.tableView_cnsList.selectedIndexes()
        if not selected_proxy_cns_indexes:
            return

        # get source index
        proxy_model: MyStandardItemAsTableModelWithoutHeader = self._ui.tableView_cnsList.model()
        target_index = proxy_model.mapToSource(selected_proxy_cns_indexes[0])

        # get row
        row = target_index.row()

        # remove
        from pyfemtet_opt_gui.cns_model import CnsModel
        cns_model: CnsModel = proxy_model.sourceModel()
        cns_model.remove_constraint(row)


# noinspection PyAttributeOutsideInit
class OptimizationWorker(QThread):
    finished = Signal()
    running = False

    def set(self, path, problem):
        self.path = path
        self.problem = problem

    def run(self):  # Override the run method to execute your long-time function
        self.running = True
        build_script_main(self.problem, self.path, True)
        self.running = False
        self.finished.emit()


def main():
    app = QApplication(sys.argv)

    g_problem: ProblemItemModel = ProblemItemModel()

    wizard = MainWizard(g_problem)

    ui_wizard = Ui_DetailedWizard()
    ui_wizard.setupUi(wizard)

    g_proxy_model = CustomProxyModel(g_problem)
    g_proxy_model.setSourceModel(g_problem)
    ui_wizard.treeView.setModel(g_proxy_model)

    wizard.set_ui(ui_wizard)  # ui を登録
    wizard.update_problem(show_warning=False)  # ui へのモデルの登録

    wizard.show()  # ビューの表示
    sys.exit(app.exec())  # アプリケーションの実行


if __name__ == '__main__':
    main()
