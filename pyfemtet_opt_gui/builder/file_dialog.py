# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from pyfemtet_opt_gui.common.return_msg import *

import os


class ScriptBuilderFileDialog(QFileDialog):

    def __init__(self, parent, f=Qt.WindowType.Dialog):
        super().__init__(parent, f)
        self.return_msg = ReturnMsg.no_message
        self.setNameFilter("Python files (*.py)")
        self.setDefaultSuffix('.py')
        self.setFileMode(QFileDialog.FileMode.AnyFile)
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

    def accept(self):
        # QDialog と違って super().accept() を呼ばないと
        # parent のウィンドウがフリーズする仕様らしいので
        # ReturnMsg だけ自身に設定してエラーハンドリングは
        # parent 側で行うことにする

        # パスを取得
        if len(self.selectedFiles()) == 0:
            # この場合はエラーではなくキャンセル
            return super().accept()

        path = self.selectedFiles()[0]

        # 拡張子を確認
        if not path.endswith('.py'):
            path += '.py'

        # ディレクトリの存在を確認
        dir_path = os.path.dirname(path)
        if not os.path.isdir(dir_path):
            self.return_msg = ReturnMsg.Error.filepath_in_not_existing_dir
            return super().accept()

        # ファイル名が python モジュールとして正しいか
        # 確認するために拡張子なしベース名を取得
        file_name = os.path.basename(os.path.splitext(path)[0])

        # 英数字又は_以外を含む
        for char in file_name:
            if char not in '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
                self.return_msg = ReturnMsg.Error.invalid_py_file_name
                return super().accept()

        # 数字で始まる
        if file_name[0] in '0123456789':
            self.return_msg = ReturnMsg.Error.invalid_py_file_name
            return super().accept()

        return super().accept()
