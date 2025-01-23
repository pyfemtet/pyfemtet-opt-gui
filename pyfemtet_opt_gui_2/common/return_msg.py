# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

import enum

__all__ = [
    'ReturnMsg',
    'show_return_msg',
    'can_continue'
]


class ReturnMsg:
    no_message = None

    class Info(enum.StrEnum):
        _test = 'This is a test information.'

    class Warn(enum.StrEnum):
        _test = 'This is a test warning message.'
        update_lb_automatically = '値と下限の関係が正しくなくなったため、下限を更新します。'
        update_ub_automatically = '値と上限の関係が正しくなくなったため、上限を更新します。'
        inconsistent_value_bounds = ('現在の初期値に基づいて計算される値と'
                                     '上下限の関係が正しくありません。最適'
                                     '化の初期値が拘束を満たさない場合、最'
                                     '適化が収束しないかエラーになる場合が'
                                     'あります。続行しますか？')
        no_params_selected = '少なくともひとつの変数を選択してください。'
        no_objs_selected = '少なくともひとつの目的関数を選択してください。'
        no_finish_conditions = '最適化の終了条件が指定されていません。この場合、手動で最適化を停止するまで計算を続けます。よろしいですか？'

    class Error(enum.StrEnum):
        _test = 'This is a test Error message.'

        # femtet
        femtet_connection_failed = 'Femtet との接続がタイムアウトしました。'
        femtet_not_found = 'Femtet のプロセスがありません。'
        femtet_connection_not_yet = 'まだ Femtet と接続されていません。'
        femtet_access_error = 'Femtet にアクセスできません。'
        femtet_macro_version_old = 'Femtet 本体または最後に実行された「マクロ機能の有効化」のバージョンが古いです。'
        cannot_open_sample_femprj = 'サンプルファイルのオープンに失敗しました'
        femtet_macro_failed = 'Femtet マクロの実行に失敗しました。'
        femprj_or_model_inconsistent = 'Femtet で開かれている解析モデルが上記のモデルと一致しません。Femtet で開かれているモデルを確認し、「Load」ボタンを押してください。'

        # expressions
        cannot_recognize_as_an_expression = '文字式の認識に失敗しました。'
        not_a_number = '数値または数式の認識に失敗しました。'
        not_a_pure_number = '数値または数式の認識に失敗しました。'
        evaluated_expression_not_float = '式が計算できないか、計算結果に実数以外の数が含まれています'  # 句読点なし
        inconsistent_lb_ub = '上下限の大小関係が正しくありません。'
        inconsistent_value_ub = '値と上限の大小関係が正しくありません。'
        inconsistent_value_lb = '値と下限の大小関係が正しくありません。'
        no_bounds = '上下限のいずれかを設定してください。'


# ReturnMsg を受け取ってダイアログ表示し
# OK かどうかを返す関数
def show_return_msg(
        return_msg: ReturnMsg,
        parent: QWidget,
        with_cancel_button=False,
        additional_message=None,
) -> bool:
    if return_msg == ReturnMsg.no_message:
        return True

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

    if additional_message is None:
        display_msg = return_msg

    else:
        display_msg = f'{return_msg}\n{additional_message}'

    if with_cancel_button:
        pressed = mb(parent, title, display_msg, QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Cancel)
        return pressed == QMessageBox.StandardButton.Ok

    else:
        # QMessageBox を OK を押さずに Esc や閉じるボタンで閉じると
        # 戻り値が QMessageBox.StandardButton.Cancel になるため
        # cancel の選択肢を与えない場合は必ず True を返すようにする
        mb(parent, title, display_msg, QMessageBox.StandardButton.Ok)
        return True


# ReturnMsg を受け取ってダイアログを表示した後
# 内部処理を進めてよいかどうかを返す関数
def can_continue(
        return_msg: ReturnMsg,
        parent: QWidget,
        with_cancel_button='auto',
        no_dialog_if_info=False,
        additional_message=None,
) -> bool:
    """
    return_msg is None -> return True
    return_msg is Info -> return True
    return_msg is Warn -> return True if accepted
    return_msg is Error -> return False
    """
    if return_msg == ReturnMsg.no_message:
        return True

    if isinstance(return_msg, ReturnMsg.Info):
        if not no_dialog_if_info:
            if with_cancel_button == 'auto':
                with_cancel_button = False
            show_return_msg(return_msg, parent, with_cancel_button, additional_message)
        return True

    elif isinstance(return_msg, ReturnMsg.Warn):
        if with_cancel_button == 'auto':
            with_cancel_button = True
        accepted = show_return_msg(return_msg, parent, with_cancel_button, additional_message)
        return accepted

    elif isinstance(return_msg, ReturnMsg.Error):
        if with_cancel_button == 'auto':
            with_cancel_button = False
        show_return_msg(return_msg, parent, with_cancel_button, additional_message)
        return False


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

        def button_clicked(self, _):

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
