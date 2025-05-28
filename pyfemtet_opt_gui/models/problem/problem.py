# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

from pyfemtet_opt_gui.ui.ui_WizardPage_confirm import Ui_WizardPage
from pyfemtet_opt_gui.common.qt_util import *
from pyfemtet_opt_gui.common.pyfemtet_model_bases import *
from pyfemtet_opt_gui.common.return_msg import *
from pyfemtet_opt_gui.common.titles import *

from pyfemtet_opt_gui.models.analysis_model.analysis_model import get_am_model_for_problem
from pyfemtet_opt_gui.models.variables.var import get_var_model_for_problem
from pyfemtet_opt_gui.models.objectives.obj import get_obj_model_for_problem
from pyfemtet_opt_gui.models.constraints.cns import get_cns_model_for_problem
from pyfemtet_opt_gui.models.config.config import get_config_model_for_problem, get_config_model

from pyfemtet_opt_gui.builder.main import create_script
from pyfemtet_opt_gui.builder.file_dialog import ScriptBuilderFileDialog
from pyfemtet_opt_gui.builder.worker import OptimizationWorker, HistoryFinder
from pyfemtet_opt_gui.surrogate_model_interfaces import SurrogateModelNames
from pyfemtet_opt_gui.logger import get_logger

import pyfemtet_opt_gui.fem_interfaces as fi

import os
import requests
from requests.exceptions import ConnectionError
from packaging.version import Version

import pyfemtet

SUB_MODELS = None
PROBLEM_MODEL = None

_REMOVING_SWEEP_WARNED = False  # スイープテーブル削除の警告

logger = get_logger()


# ===== rules =====
def get_sub_models(parent) -> dict[str, QStandardItemModel]:
    global SUB_MODELS
    if SUB_MODELS is None:
        assert parent is not None
        SUB_MODELS = dict(
            femprj=get_am_model_for_problem(parent=parent),
            parameters=get_var_model_for_problem(parent=parent),
            objectives=get_obj_model_for_problem(parent=parent),
            constraints=get_cns_model_for_problem(parent=parent),
            config=get_config_model_for_problem(parent=parent),
        )
    return SUB_MODELS


def get_problem_model(parent=None) -> 'ProblemTableItemModel':
    global PROBLEM_MODEL
    if PROBLEM_MODEL is None:
        PROBLEM_MODEL = ProblemTableItemModel(parent=parent)
    return PROBLEM_MODEL


# ===== objects =====
class ProblemTableItemModel(StandardItemModelWithEnhancedFirstRow):
    sub_models: dict[str, QStandardItemModel]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.root = self.invisibleRootItem()
        self.sub_models = get_sub_models(parent=parent)

        with EditModel(self):
            # 各サブモデルごとに setChild する
            for i, (key, model) in enumerate(self.sub_models.items()):
                # item に変換
                item = StandardItemModelAsQStandardItem(key, model)

                # setChild
                self.root.setChild(i, 0, item)

                # カラム数をサブモデルの最大値に設定
                self.root.setColumnCount(
                    max(
                        self.root.columnCount(),
                        item.columnCount()
                    )
                )

    def flags(self, index):
        return super().flags(index) & ~Qt.ItemFlag.ItemIsEditable & ~Qt.ItemFlag.ItemIsUserCheckable


class QProblemItemModelWithoutUseUnchecked(QSortFilterProxyModelOfStandardItemModel):
    pass


class ConfirmWizardPage(TitledWizardPage):
    ui: Ui_WizardPage
    source_model: ProblemTableItemModel
    proxy_model: QProblemItemModelWithoutUseUnchecked
    column_resizer: ResizeColumn
    worker: OptimizationWorker
    history_finder: HistoryFinder

    page_name = PageSubTitles.confirm

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = OptimizationWorker(self.parent())
        self.history_finder = HistoryFinder(self.worker)
        self.setup_ui()
        self.setup_model()
        self.setup_view()
        self.setup_signal()

    def setup_ui(self):
        self.ui = Ui_WizardPage()
        self.ui.setupUi(self)

    def setup_model(self):
        self.source_model = get_problem_model(parent=self)
        self.proxy_model = QProblemItemModelWithoutUseUnchecked(self)
        self.proxy_model.setSourceModel(self.source_model)

    def setup_view(self):
        view = self.ui.treeView
        view.setModel(self.proxy_model)
        view.expandAll()

        self.column_resizer = ResizeColumn(view)
        self.column_resizer.resize_all_columns()

    def setup_signal(self):
        # 「スクリプトを保存する」を実行するとスクリプトを保存する
        self.ui.pushButton_save_script.clicked.connect(
            self.save_script
        )

        # 最適化の開始・終了時のシグナル
        self.worker.started.connect(lambda: self.switch_save_script_button(True))
        self.worker.finished.connect(lambda: self.switch_save_script_button(False))
        self.worker.started.connect(lambda: self.switch_explanation_text('started'))
        self.worker.finished.connect(lambda: self.switch_explanation_text('finished'))

        # history finder の開始・終了時のシグナル
        self.history_finder.finished.connect(lambda: self.switch_explanation_text('history found'))

    def save_script(self):
        global _REMOVING_SWEEP_WARNED

        # 保存ファイル名を決めてもらう
        selected_file = None
        while True:
            # ダイアログを作成
            dialog = ScriptBuilderFileDialog(parent=self)

            # 以前の file 名指定が残っていれば復元
            if selected_file is not None:
                dialog.selectFile(selected_file)

            # ダイアログを実行（modal, blocking)
            dialog.exec()

            # ファイルパスを取得 (長さ 0 or 1)
            selected_files = dialog.selectedFiles()

            # 命名違反でなければ抜ける
            if can_continue(dialog.return_msg, self):
                break

            # 命名違反であれば selected_file を保存してもう一度
            else:
                assert len(selected_files) != 0
                selected_file = selected_files[0]

        # 保存ファイル名が指定しなければ
        # キャンセルと見做して何もしない
        if len(selected_files) == 0:
            return

        # スイープテーブルが削除される旨を警告
        if not _REMOVING_SWEEP_WARNED:
            # TODO: 永続化する
            if can_continue(
                    ReturnMsg.Warn.notify_to_sweep_table_remove,
                    parent=self,
            ):
                # 了解したものとして起動中今後は警告しない
                _REMOVING_SWEEP_WARNED = True

            else:
                # 了解を得られなかったので実行しない
                return

        # サロゲートモデルを作成するかどうかで処理を変更
        config_model = get_config_model(self)
        if config_model.get_surrogate_model_name() == SurrogateModelNames.no:

            # スクリプトを保存する
            path = selected_files[0]
            create_script(path)

            # 「保存後すぐ実行する」にチェックがあれば実行する
            should_run = self.ui.checkBox_save_with_run.checkState() == Qt.CheckState.Checked
            if should_run:
                history_path = config_model.history_path
                assert history_path is not None
                self.start_run_script_thread((path,), (history_path,))

        else:
            # スクリプトを保存する
            user_defined_path = selected_files[0]
            pre, post = os.path.splitext(user_defined_path)
            training_py_path = pre + post  # create_script で「ファイル名 + _訓練データ.csv」を指定するので何か入れると不自然
            optimize_py_path = pre + '_optimize' + post

            # ユーザーは history_path を指定していない可能性があり、
            # そのような場合は create_script 内で history_path が
            # 確定する
            create_script(training_py_path)
            history_path_1 = config_model.history_path
            assert history_path_1 is not None
            config_model.reset_history_path()

            create_script(optimize_py_path, use_surrogate=True)
            history_path_2 = config_model.history_path
            assert history_path_2 is not None

            history_paths = (
                history_path_1,
                history_path_2
            )

            # 「保存後すぐ実行する」にチェックがあれば実行する
            should_run = self.ui.checkBox_save_with_run.checkState() == Qt.CheckState.Checked
            if should_run:

                should_run_after_confirm = True

                # 2 回実行することを通知する
                if not can_continue(
                    ReturnMsg.Info.run_twice_in_surrogate,
                    parent=self,
                    no_dialog_if_info=False,
                    with_cancel_button=True,
                ):
                    should_run_after_confirm = False

                # 終了条件が未指定なら警告もする
                if config_model.is_no_finish_conditions():
                    if not can_continue(
                            ReturnMsg.Warn.no_finish_conditions_in_surrogate_optimization,
                            parent=self,
                    ):
                        should_run_after_confirm = False

                if should_run_after_confirm:
                    self.start_run_script_thread(
                        (training_py_path, optimize_py_path),
                        history_paths
                    )

    def start_run_script_thread(self, py_paths, history_paths):
        fi.get().save_femprj()

        self.worker.set_paths(py_paths)
        self.history_finder.set_paths(history_paths, py_paths)

        # worker は history の初期化(signal connect)の後に
        # 実行する必要がある
        self.worker.start()
        self.history_finder.start()

    def switch_save_script_button(self, running: bool):
        # worker が実行ならば button を disabled にするなど
        button = self.ui.pushButton_save_script

        if running:
            # version 0.8.6 以降、この GUI 経由で最適化を停止できる
            if Version(pyfemtet.__version__) >= Version("0.8.5"):
                button.clicked.disconnect(self.save_script)
                button.clicked.connect(self.stop_optimization)
                button.setText('現在の解析を最後にして最適化を停止する')

            else:
                button.setText('最適化の実行中はスクリプトを保存できません')
                button.setDisabled(True)

        else:
            if Version(pyfemtet.__version__) >= Version("0.8.5"):
                # signal を元に戻す
                button.clicked.disconnect(self.stop_optimization)
                button.clicked.connect(self.save_script)

                # output_json で set したhistory_path の
                # 情報を model から消す（初期化）
                model = get_config_model_for_problem(self)
                # model.reset_history_path()  # このスレッドで reset してはいけないかも

            # 元に戻す
            button.setText(button.accessibleName())
            button.setDisabled(False)

    def switch_explanation_text(self, state: str):
        # worker が実行ならば button を disabled にするなど
        text_edit: QTextBrowser = self.ui.textBrowser

        # FIXME:
        #   変な終了の仕方をして
        #   optimization worker が終了してから
        #   history が見つかると assertion error が
        #   起こってしまう
        if state == 'started':
            buff = text_edit.toHtml()
            text_edit._buff = buff

            # 再実行時、html のフォーマットが残留することが
            # あったので document を使って初期化
            doc = QTextDocument()
            doc.setPlainText('開始しています。1 分程度お待ちください。\n'
                             '最適化が始まるとプロセスモニターを起動します。\n'
                             '最適化の確認・中断はプロセスモニターから行います。')
            text_edit.setDocument(doc)

        elif state == 'history found':

            # version 0.8.6 以降、host 情報にアクセスできる
            proxy_model = get_config_model_for_problem(self)
            data, ret_msg = proxy_model.get_monitor_host_info()

            text = (f'\nブラウザで上の URL にアクセスすると'
                    f'プロセスモニターを開くことができます。')

            if Version(pyfemtet.__version__) < Version('0.8.6'):
                from pyfemtet.opt.visualization._process_monitor.application import ProcessMonitorApplication
                port = ProcessMonitorApplication.DEFAULT_PORT
                url = f'http://localhost:{port}'
                text = text + '※ pyfemtet のバージョンが古いのでデフォルトのポート値を取得しています。\n'

            else:

                if ret_msg == ReturnMsg.no_message:
                    url = f'http://{data["host"]}:{data["port"]}'

                else:
                    url = f'http://localhost:8080'
                    text = text + '※ ポート情報の取得に失敗したのでデフォルトのポート値を取得しています。\n'

            text += (f'最適化が停止したらコンソール画面で「Enter」を押してください。\n'
                     f'それまでの間はモニターを停止しないので分析作業を行うことができます。')

            text_edit.setText(text)

            # setText の後に cursor は始点にある？
            text_edit.insertHtml(
                f'<p style='
                f'" margin-top:0px;'
                f' margin-bottom:0px;'
                f' margin-left:0px;'
                f' margin-right:0px;'
                f' -qt-block-indent:0;'
                f' text-indent:0px;">'
                f'<a href="{url}">'
                f'<span style="'
                f' text-decoration: underline;'
                f' color:#c7bba5;">'
                f'{url}</span></a></p></body></html>'
            )

        elif state == 'finished':
            # 元に戻す
            text_edit.setHtml(text_edit._buff)

        else:
            raise NotImplementedError

    def stop_optimization(self):
        # port record が存在するかチェックする
        proxy_model = get_config_model_for_problem(self)

        # 最新版にアップデートしなければ使えない
        # またはまだ最適化が始まっていない
        host_info, ret_msg = proxy_model.get_monitor_host_info()
        if not can_continue(ret_msg, parent=self):
            return

        host = host_info['host']
        port = host_info['port']

        try:
            response = requests.get(f'http://{host}:{port}/interrupt')

            # info をメッセージする
            if response.status_code == 200:
                # print("Success:", response.json())
                ret_msg = ReturnMsg.Info.interrupt_signal_emitted
                show_return_msg(ret_msg, parent=self)

            # error をメッセージする
            else:
                # print("Failed to execute command.")
                ret_msg = ReturnMsg.Error.failed_to_emit_interrupt_signal
                show_return_msg(ret_msg, parent=self)

        # error をメッセージする
        except ConnectionError:
            # print("Failed to connect server.")
            ret_msg = ReturnMsg.Error.failed_to_connect_process_monitor
            show_return_msg(ret_msg, parent=self)

    def validatePage(self) -> bool:

        if self.worker.isRunning():
            ret_msg = ReturnMsg.Error.cannot_finish_during_optimization

        else:
            ret_msg = ReturnMsg.Warn.confirm_finish

        return can_continue(ret_msg, parent=self)


if __name__ == '__main__':
    import sys
    from pyfemtet_opt_gui.models.objectives.obj import ObjectiveWizardPage
    from pyfemtet_opt_gui.models.variables.var import VariableWizardPage
    from pyfemtet_opt_gui.models.config.config import ConfigWizardPage
    from pyfemtet_opt_gui.models.constraints.cns import ConstraintWizardPage
    from pyfemtet_opt_gui.models.analysis_model.analysis_model import AnalysisModelWizardPage

    fi.get().get_femtet()

    app = QApplication()
    app.setStyle('fusion')

    # page_cfg = ConfigWizardPage()
    # page_cfg.show()
    #
    # page_obj = ObjectiveWizardPage()
    # page_obj.show()
    #
    # page_var = VariableWizardPage()
    # page_var.show()
    #
    # page_cns = ConstraintWizardPage()
    # page_cns.show()
    #
    # page_am = AnalysisModelWizardPage()
    # page_am.show()

    page_main = ConfirmWizardPage()
    page_main.show()

    sys.exit(app.exec())
