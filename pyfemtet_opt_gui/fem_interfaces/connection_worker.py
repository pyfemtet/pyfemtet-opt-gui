import enum

# noinspection PyUnresolvedReferences
from pythoncom import CoInitialize, CoUninitialize

# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from pyfemtet_opt_gui.common.return_msg import *

from pyfemtet_opt_gui.ui import ui_Wizard_main
import pyfemtet_opt_gui.fem_interfaces as fi


__all__ = [
    'ConnectionMessage',
    'ConnectionWorker',
]


class QThreadWithReturnMsg(QThread):
    finished = Signal(str)

    def emit_return_code(self, ret_msg: ReturnType):
        ret_code = ReturnMsg.encode(ret_msg)
        self.finished.emit(ret_code)


class ConnectionMessage(enum.StrEnum):
    no_connection = '接続されていません。'
    connecting = '接続可能な Femtet を探しています...\n見つからない場合は起動して接続します...'
    connected = '接続されています。'


class ConnectionWorker(QThreadWithReturnMsg):

    def __init__(
            self,
            parent,
            ui: ui_Wizard_main,
            progress: QProgressDialog = None,
    ):
        super().__init__(parent)
        self.ui: ui_Wizard_main = ui
        self.progress: QProgressDialog | None = progress

    def run(self):

        CoInitialize()

        # Femtet との接続がすでに OK
        ret: ReturnMsg = fi.get().get_connection_state()
        if ret == ReturnMsg.no_message:
            self.update_connection_state_label(ConnectionMessage.connected)

        # Femtet との接続が NG
        else:
            # 接続開始
            self.update_connection_state_label(ConnectionMessage.connecting)

            # Femtet との接続を開始する
            # Femtet の接続ができるのを待つ
            _, ret_msg = fi.get().get_femtet(self.progress)

            if ret_msg != ReturnMsg.no_message:
                self.update_connection_state_label(ConnectionMessage.no_connection)
                self.emit_return_code(ret_msg)
                return

            # 接続成功
            self.update_connection_state_label(ConnectionMessage.connected)

        # 必要なら sample file を開く
        if (
                fi.get().get_connection_state() == ReturnMsg.no_message
                and self.ui.checkBox_openSampleFemprj.isChecked()
        ):
            ret_msg, path = fi.get().open_sample(self.progress)

            # 開くのに失敗
            if ret_msg != ReturnMsg.no_message:
                self.emit_return_code(ret_msg)
                return

        # 終了
        self.emit_return_code(ReturnMsg.no_message)
        return

    def update_connection_state_label(self, connection_message: ConnectionMessage):

        label: QLabel = self.ui.label_connectionState

        if label is None:
            return

        assert isinstance(label, QLabel)

        label.setText(connection_message)
        if connection_message == ConnectionMessage.no_connection:
            label.setStyleSheet('color: red')

        elif connection_message == ConnectionMessage.connecting:
            label.setStyleSheet('color: red')

        elif connection_message == ConnectionMessage.connected:
            label.setStyleSheet('color: green')
