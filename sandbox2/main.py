import sys

from PySide6.QtWidgets import (QApplication, QWizard)
from PySide6.QtCore import (Slot, Signal)

from ui_wizard import Ui_Wizard
from table_model import PrmTableModel, ObjTableModel, ComboBoxDelegate


import _p


# noinspection PyMethodMayBeStatic
class MainWizard(QWizard):

    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def set_ui(self, ui):
        # noinspection PyAttributeOutsideInit
        self._ui = ui

    def load_prm(self):
        if self._ui.plainTextEdit_prj.toPlainText():
            prm_table_model = PrmTableModel()  # モデルの作成
            self._ui.tableView_prm.setModel(prm_table_model)  # モデルをビューに設定

    def load_obj(self):
        if self._ui.plainTextEdit_prj.toPlainText():
            obj_table_model = ObjTableModel()  # モデルの作成
            self._ui.tableView_obj.setModel(obj_table_model)  # モデルをビューに設定
            delegate = ComboBoxDelegate(obj_table_model)  # デリゲートの作成
            ui_wizard.tableView_obj.setItemDelegate(delegate)  # デリゲートをビューに設定

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
            _p.logger.warning('Femtet との接続が確立していません。')

    def connect_process(self):
        if _p.connect_femtet():
            _p.logger.info(f'Connected! (pid: {_p.pid})')  # TODO: show dialog

            # update model
            self.update_model_via_ui()

        else:
            _p.logger.warning('Connection failed.')

    def update_model_via_ui(self):
        if self._ui.plainTextEdit_prj.toPlainText():
            self.load_prm()
            self.load_obj()
            self.load_model()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    wizard = MainWizard()

    ui_wizard = Ui_Wizard()
    ui_wizard.setupUi(wizard)

    ####### TEST CODE FOR EMBED COMBOBOX TO TABLEVIEW ################################
    # from PySide6.QtWidgets import QComboBox
    # c = QComboBox()
    # c.addItem('Maximize')
    # c.addItem('Minimize')
    # c.addItem('Specify')
    # index = obj_table_model.createIndex(0, 2)
    # ui_wizard.tableView_obj.setIndexWidget(index, c)
    ####### EMBEDDING SUCCESSFULLY, BUT setData and data couldn't be implemented ####

    wizard.set_ui(ui_wizard)  # ui を登録
    wizard.update_model_via_ui()  # ui へのモデルの登録

    wizard.show()  # ビューの表示
    sys.exit(app.exec())  # アプリケーションの実行
