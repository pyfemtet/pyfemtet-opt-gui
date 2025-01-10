# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *


import enum


class ReturnMsg:
    no_message = ''

    class Info(enum.StrEnum):
        _test = 'This is a test information.'

    class Warn(enum.StrEnum):
        _test = 'This is a test warning message.'

    class Error(enum.StrEnum):
        _test = 'This is a test Error message.'
        femtet_not_found = 'Femtet のプロセスがありません。'
        femtet_connection_not_yet = 'まだ Femtet と接続されていません。'
        femtet_access_error = 'Femtet にアクセスできません。'
        femtet_macro_version_old = 'Femtet 本体または最後に実行された「マクロ機能の有効化」のバージョンが古いです。'
        evaluated_expression_not_float = '式が計算できないか、計算結果に実数以外の数が含まれています'  # 句読点なし


# ReturnMsg を受け取ってダイアログ表示し
# OK かどうかを返す関数
def show_return_msg(
        return_msg: ReturnMsg,
        parent=None,
        with_cancel_button=False
) -> bool:

    if isinstance(return_msg, ReturnMsg.Info):
        mb = QMessageBox.information
        title = 'Info'

    elif isinstance(return_msg, ReturnMsg.Warn):
        mb = QMessageBox.warning
        title = 'Warning'

    elif isinstance(return_msg, ReturnMsg.Error):
        mb = QMessageBox.critical
        title = 'Error!'

    else:
        raise NotImplementedError


    if with_cancel_button:
        pressed = mb(parent, title, return_msg, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel)
        return pressed == QMessageBox.StandardButton.Ok

    else:
        # QMessageBox を OK を押さずに Esc や閉じるボタンで閉じると
        # 戻り値が QMessageBox.StandardButton.Cancel になるため
        # cancel の選択肢を与えない場合は必ず True を返すようにする
        mb(parent, title, return_msg, QMessageBox.StandardButton.Ok)
        return True


# basic behavior
if __name__ == '__main__':

    def some_fun() -> ReturnMsg:
        # return ReturnMsg.no_message
        return ReturnMsg.Info._test
        # return ReturnMsg.Warn._test
        # return ReturnMsg.Error._test

    return_msg_ = some_fun()

    if return_msg_:

        if isinstance(return_msg_, ReturnMsg.Info):
            print(return_msg_)

        elif isinstance(return_msg_, ReturnMsg.Warn):
            print(return_msg_)

        elif isinstance(return_msg_, ReturnMsg.Error):
            print(return_msg_)

        else:
            raise NotImplementedError


# basic usage
if __name__ == '__main__':

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()

            self.setWindowTitle("My App")

            button = QPushButton("Press me for a dialog!")
            button.clicked.connect(self.button_clicked)
            self.setCentralWidget(button)

        def button_clicked(self, s):

            return_msg = some_fun()

            parent = self

            if return_msg:
                accepted = show_return_msg(return_msg, parent, with_cancel_button=False)
                if accepted:
                    print("The OK button is pressed (or only OK button is shown).")
                else:
                    print("The OK button is not pressed.")

            else:
                print('There is no message.')


    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec()
