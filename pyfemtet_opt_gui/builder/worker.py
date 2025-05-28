import os
from time import sleep, time

# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from traceback import print_exception


class HistoryFinder(QThread):

    def __init__(self, parent):
        assert isinstance(parent, OptimizationWorker)
        super().__init__(parent)

        self.optim_worker = parent
        self.optim_worker.process_started.connect(self.on_process_started)

    def set_paths(self, history_paths, py_paths):
        self.history_paths = history_paths
        self.paths = py_paths
        self._process_started_flags = {p: False for p in self.paths}

    def on_process_started(self, path):
        assert path in self._process_started_flags
        self._process_started_flags[path] = True

    def run(self):
        for path, history_path in zip(self.paths, self.history_paths):

            # worker の処理開始を待つ
            while not self._process_started_flags.get(path, False):
                # 続きからの場合 history_path はすでに存在する可能性があるので
                # ここで何かを print してはいけない。
                sleep(1)

            # history_path を UI に通知するついでに
            # 起動までのカウントアップを行う。
            # history_path は最適化前にすでに存在する可能性もあるので
            # 目安
            s = time()
            while not os.path.exists(history_path):
                sleep(1)
                print(f'立上げからの経過時間: {int(time()-s)} 秒')
            print(f'最適化が開始されます。')


class OptimizationWorker(QThread):
    paths: list[str]
    process_started = Signal(str)

    def set_paths(self, script_paths):
        self.paths = script_paths

    def run(self):
        # Femtet との接続は一度に一プロセスで、
        # 現在のプロセスが解放されない限り新しい
        # Femtet が必要なので現在のプロセスで実行する

        # 以下の方法は PyFemtet 内でファイルが存在する
        # ことを前提に inspect などで処理する機能が
        # 動作しないので実装してはいけない
        # exec(code)

        for path in self.paths:

            self.process_started.emit(path)

            print()
            print('================================')
            print(f'最適化プログラムを開始します。')
            print(f'ターゲットファイル: {path}')
            print(f'Femtet の自動制御を開始します。\nしばらくお待ちください。')
            print()

            import os
            import sys
            import importlib

            script_place, script_name = os.path.split(path)
            module_name = os.path.splitext(script_name)[0]

            os.chdir(script_place)
            sys.path.append(script_place)
            try:
                # from <module_name> import * を常に reload で行う
                if module_name in sys.modules:
                    module = importlib.reload(sys.modules[module_name])
                else:
                    module = importlib.import_module(module_name)
                module_members = [name for name in dir(module) if not name.startswith('_')]
                globals().update({name: getattr(module, name) for name in module_members})
                getattr(module, 'main')()

                print('================================')
                print('終了しました。')
                print('================================')

            except Exception as e:
                print_exception(e)
                print()
                print('================================')
                print('エラー終了しました。')
                print('================================')
