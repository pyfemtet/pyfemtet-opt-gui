# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from traceback import print_exception


# noinspection PyAttributeOutsideInit
class OptimizationWorker(QThread):

    def __init__(self, parent, script_path):
        super().__init__(parent)
        self.path = script_path

    def run(self):  # Override the run method to execute your long-time function
        # Femtet との接続は一度に一プロセスで、
        # 現在のプロセスが解放されない限り新しい
        # Femtet が必要なので現在のプロセスで実行する

        # 以下の方法は PyFemtet 内でファイルが存在する
        # ことを前提に inspect などで処理する機能が
        # 動作しないので実装してはいけない
        # exec(code)

        print()
        print('================================')
        print(f'最適化プログラムを開始します。')
        print(f'ターゲットファイル: {self.path}')
        print(f'Femtet の自動制御を開始します。\nしばらくお待ちください。')
        print()

        import os
        import sys

        script_place, script_name = os.path.split(self.path)
        module_name = os.path.splitext(script_name)[0]

        os.chdir(script_place)
        sys.path.append(script_place)
        try:
            exec(f'from {module_name} import *; main()', {}, {})

            print('================================')
            print('終了しました。')
            print('================================')

        except Exception as e:
            print_exception(e)
            print()
            print('================================')
            print('エラー終了しました。')
            print('================================')
