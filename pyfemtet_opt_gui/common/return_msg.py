from __future__ import annotations

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
    'can_continue',
    'ReturnType'
]


class ReturnMsg:
    no_message = None

    class Info(enum.StrEnum):
        _test = 'This is a test information.'

        interrupt_signal_emitted = '中断信号を送信しました。現在の解析を最後に最適化を終了します。'
        run_twice_in_surrogate = ('サロゲートモデルを用いた最適化をする場合、'
                                  'まず Femtet を使って訓練データを作成し、'
                                  '次にサロゲートモデルが訓練データを参照して'
                                  '最適化を行います。\n'
                                  'OK を押すと訓練データ作成を開始し、'
                                  'それが終了すると自動的に最適化を開始します。')

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
        notify_to_sweep_table_remove = ('最適化実施時、対象の解析モデルからはパラメトリック解析のスイープテーブルが削除されます。\n'
                                        '必要な場合、femprj ファイルのコピーを保存してから実行してください。\n'
                                        'このまま進めてもよろしいですか？')
        confirm_finish = '最適化スクリプト作成・実行を終了しますか？'
        no_finish_conditions_in_surrogate_optimization = ('最適化の終了条件が指定されていません。'
                                                          'この場合、訓練データの作成は手動停止まで継続し、'
                                                          'その後さらにサロゲートモデルを用いた最適化が始まり、'
                                                          '手動停止まで継続されます。'
                                                          'このまま進めてもよろしいですか？')
        confirm_delete_constraint = '拘束式を削除してよろしいですか？この操作は取り消せません。: '

    class Error(enum.StrEnum):
        _test = 'This is a test Error message.'
        internal = 'Internal Error!'

        # femtet
        femtet_connection_failed = 'Femtet との接続がタイムアウトしました。'
        femtet_not_found = 'Femtet のプロセスがありません。'
        femtet_connection_not_yet = 'まだ Femtet と接続されていません。'
        femtet_access_error = 'Femtet にアクセスできません。'
        femtet_macro_version_old = 'Femtet 本体または最後に実行された「マクロ機能の有効化」のバージョンが古いです。'
        cannot_open_sample_femprj = 'サンプルファイルのオープンに失敗しました'
        femtet_macro_failed = 'Femtet マクロの実行に失敗しました。'
        femprj_or_model_inconsistent = 'Femtet で開かれている解析モデルが上記のモデルと一致しません。Femtet で開かれているモデルを確認し、「Load」ボタンを押してください。'
        femtet_save_failed = 'femprj ファイルの保存に失敗しました。'
        femtet_no_cad_import = 'Femtet プロジェクトに CAD インポートコマンドが見つかりませんでした。まず Femtet で CAD インポートを行って解析条件設定を行ってください。'

        # expressions
        cannot_recognize_as_an_expression = '文字式の認識に失敗しました。'
        not_a_number = '数値または数式の認識に失敗しました。'
        not_a_number_expression_setting_is_enable_in_constraint = '数値が入力されていません。計算式を設定したい場合、「拘束式の設定」ページで設定してください。。'
        not_a_pure_number = '数値を入力してください。'
        unknown_var_name = '次の変数が不明な変数を参照しています'
        evaluated_expression_not_float = '式が計算できないか、計算結果に実数以外の数が含まれています'  # 句読点なし
        inconsistent_lb_ub = '上下限の大小関係が正しくありません。'
        inconsistent_value_ub = '値と上限の大小関係が正しくありません。'
        inconsistent_value_lb = '値と下限の大小関係が正しくありません。'
        no_bounds = '上下限のいずれかを設定してください。'
        step_must_be_positive = 'step は正の数でなければなりません。'
        raises_other_expression_error = 'この変更によって、別の式にエラーが発生します。'

        # others
        duplicated_constraint_name = '拘束式名が既存のものと重複しています。別の名前を指定してください。'
        filepath_in_not_existing_dir = '存在しないフォルダのファイルパスが指定されました。'
        invalid_py_file_name = 'ファイル名は以下の条件を満たしてください。\n- 半角英数字又は _ 以外を含まない\n- 数字で始まらない'
        invalid_file_name = 'ファイルパスに使用できない文字が含まれています。'
        history_path_not_found = '記録 csv ファイルが見つかりません。まだ最適化が始まっていない可能性があります。お手数ですが、最適化が始まってから中断を行ってください。'
        host_info_not_found = ('記録 csv にプロセスモニターのポート情報が見つかりません。pyfemtet のバージョンが古い可能性があります。\n'
                               '最適化を中断する場合は、ブラウザでプロセスモニターにアクセス（既定は「http://localhost:8080」）して'
                               '中断ボタンを押してください。')
        failed_to_emit_interrupt_signal = ('最適化終了信号を送信しましたが、エラーが発生しました。最適化が始まっていないか可能性があります。\n'
                                           '最適化が始まっていない場合は、お手数ですが最適化が始まってから中断を行ってください。\n'
                                           '最適化が始まっているのにこのエラーが表示される場合は、ブラウザでプロセスモニターにアクセス（既定は「http://localhost:8080」）して'
                                           '中断ボタンを押してください。')
        failed_to_connect_process_monitor = ('プロセスモニターのポートが見つかりませんでした。最適化が開始されていないか、ポート情報が間違っている可能性があります。\n'
                                             '最適化を中断する場合は、ブラウザでプロセスモニターにアクセス（既定は「http://localhost:8080」）して'
                                             '中断ボタンを押してください。')
        cannot_finish_during_optimization = '最適化の実行中は終了できません。先に最適化を終了してください。'
        no_selection = '何も選択されていません。'
        no_such_constraint = '拘束式が見つかりませんでした。: '

        # solidworks
        sw_process_not_found = 'Solidworks のプロセスがありません。'
        sw_connection_not_yet = 'まだ Solidworks と接続されていません。'
        sw_connection_error = 'Solidworks のプロセスと接続できていません。'
        sw_no_active_doc = 'Solidworks のアクティブなモデルがありません。'
        sw_model_error = 'Solidworks のモデル再構築に失敗しました。'
        sw_cannot_export_model = 'Solidworks モデルの .x_t ファイル保存がタイムアウトしました。'
        sw_remaining_variable = 'Solidworks モデルに登録されていない変数が転送されました。Solidworks で意図しないモデルが開かれている可能性があります。'
        sw_sldprt_not_found = '開かれている Solidworks モデルの .sldprt ファイルパスが見つかりません。'

    @classmethod
    def encode(cls, value: enum.StrEnum | None) -> str:

        if value == cls.no_message:
            return ''

        # noinspection PyUnresolvedReferences
        if isinstance(value, cls.Info):
            prefix = 'I'
        elif isinstance(value, cls.Warn):
            prefix = 'W'
        elif isinstance(value, cls.Error):
            prefix = 'E'
        else:
            raise NotImplementedError

        return f'{prefix}{value.name}'

    @classmethod
    def parse_code(cls, code: str) -> 'ReturnType':
        assert isinstance(code, str)

        if code == '':
            ret = cls.no_message

        else:
            prefix = code[0]
            name = code[1:]

            if prefix == 'I':
                E = cls.Info
            elif prefix == 'W':
                E = cls.Warn
            elif prefix == 'E':
                E = cls.Error
            else:
                raise NotImplementedError

            if name in E._member_map_:
                # noinspection PyTypeChecker
                ret = E._member_map_[name]
            else:
                raise NotImplementedError('Invalid message.')

        assert (
            ret == ReturnMsg.no_message
            or isinstance(ret, cls.Info)
            or isinstance(ret, cls.Warn)
            or isinstance(ret, cls.Error)
        )

        return ret

    @classmethod
    def verify_return_message(cls, code_or_ret: str | ReturnType) -> ReturnType:

        if (
                code_or_ret == cls.no_message
                or isinstance(code_or_ret, cls.Info)
                or isinstance(code_or_ret, cls.Warn)
                or isinstance(code_or_ret, cls.Error)
        ):
            return code_or_ret

        else:
            return cls.parse_code(code_or_ret)


ReturnType = ReturnMsg.Error | ReturnMsg.Warn | ReturnMsg.Info | ReturnMsg.no_message


# ReturnMsg を受け取ってダイアログ表示し
# OK かどうかを返す関数
def show_return_msg(
        return_msg: ReturnMsg | ReturnMsg.Info | ReturnMsg.Warn | ReturnMsg.Error | str,
        parent: QWidget,
        with_cancel_button=False,
        additional_message=None,
) -> bool:

    return_msg = ReturnMsg.verify_return_message(return_msg)

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
        return_msg: ReturnMsg | ReturnMsg.Info | ReturnMsg.Warn | ReturnMsg.Error | str,
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

    return_msg = ReturnMsg.verify_return_message(return_msg)

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

    def some_fun() -> ReturnMsg | ReturnMsg.Info | ReturnMsg.Warn | ReturnMsg.Error:
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
