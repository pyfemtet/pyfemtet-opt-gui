"""
モデル初期値・行列アクセス
終了条件の有無
アルゴリズム切替によるサブモデル切替
history_pathの自動生成・リセット・取得
JSON出力内容
Delegateでの値チェック（数値/文字列/異常値）
サロゲートモデル名取得
validatePageでの警告/分岐
Problem用Proxyのカラムフィルタ・history_path取得・monitor_host_info取得

"""
from PySide6.QtWidgets import QLineEdit, QStyleOptionViewItem

from pyfemtet_opt_gui.common.qt_util import *

import pytest
import datetime
import json
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot


import pyfemtet_opt_gui.models.config.config as cfg_mod  # for monkeypatch
from pyfemtet_opt_gui.models.config.config import (
    get_config_model, ConfigItemModel, ConfigWizardPage, QConfigItemModelForProblem, ConfigHeaderNames,
    ConfigItemClassEnum, _reset_config_model
)
from pyfemtet_opt_gui.common.return_msg import ReturnMsg
from pyfemtet_opt_gui.surrogate_model_interfaces import SurrogateModelNames


@pytest.fixture(autouse=True)
def reset_config_model():
    import pyfemtet_opt_gui.models.config.config as config_mod
    config_mod._CONFIG_MODEL = None
    config_mod._CONFIG_MODEL_FOR_PROBLEM = None
    _start_debugging()
    yield
    _end_debugging()
    config_mod._CONFIG_MODEL = None
    config_mod._CONFIG_MODEL_FOR_PROBLEM = None


@pytest.fixture
def page(qtbot):
    _reset_config_model()
    page = ConfigWizardPage()
    qtbot.addWidget(page)
    page.show()
    qtbot.waitExposed(page)

    _start_debugging()
    yield page
    _end_debugging()

    page.close()
    _reset_config_model()


def test_config_model_initialization():
    print("""
    最適化設定の初期値をチェック
    """)
    model = get_config_model(parent=None)
    c = model.get_column_by_header_data(ConfigHeaderNames.value)
    r = model.get_row_by_header_data(ConfigItemClassEnum.n_trials.value.name)
    val = model.item(r, c).data(Qt.ItemDataRole.UserRole)
    print(f"n_trials value(user role): {val}")
    assert val == 20
    print()


def test_is_no_finish_conditions(monkeypatch):
    print("""
    最適化設定で終了条件が指定されていない場合が
    検出できることを確認
    """)
    model = get_config_model(parent=None)
    c = model.get_column_by_header_data(ConfigHeaderNames.value)
    r1 = model.get_row_by_header_data(ConfigItemClassEnum.n_trials.value.name)
    model.item(r1, c).setData(None, Qt.ItemDataRole.UserRole)
    r2 = model.get_row_by_header_data(ConfigItemClassEnum.timeout.value.name)
    model.item(r2, c).setData(None, Qt.ItemDataRole.UserRole)
    result = model.is_no_finish_conditions()
    print(f"is_no_finish_conditions (both None): {result}")
    assert result
    model.item(r1, c).setData(100, Qt.ItemDataRole.UserRole)
    result2 = model.is_no_finish_conditions()
    print(f"is_no_finish_conditions (n_trials=100): {result2}")
    assert not result2
    print()


def test_algorithm_switch(monkeypatch):
    print("""
    アルゴリズムを入力して変更できることを確認
    """)
    model = get_config_model(parent=None)
    c = model.get_column_by_header_data(ConfigHeaderNames.value)
    r = model.get_row_by_header_data(ConfigItemClassEnum.algorithm.value.name)
    item = model.item(r, c)
    old_submodel = model.algorithm_model
    # Switch to a different algorithm
    for key in ConfigItemClassEnum.algorithm.value.choices.keys():
        if key != item.data(Qt.ItemDataRole.DisplayRole):
            item.setText(key)
            break
    model.check_update_algorithm(model.index(r, c), model.index(r, c), [Qt.ItemDataRole.DisplayRole])
    print(f"Old algorithm_model: {old_submodel}, New algorithm_model: {model.algorithm_model}")
    assert model.algorithm_model is not old_submodel
    print()


def test_history_path_auto_and_reset(monkeypatch):
    print("""
    履歴 csv のパスが自動生成出来ることを確認
    """)
    model = get_config_model(parent=None)
    model._history_path = None
    c = model.get_column_by_header_data(ConfigHeaderNames.value)
    r = model.get_row_by_header_data(ConfigItemClassEnum.history_path.value.name)
    model.item(r, c).setData('', Qt.ItemDataRole.DisplayRole)
    path = model._ConfigItemModel__certify_and_get_history_path()
    print(f"Auto-generated history_path: {path}")
    assert path.endswith('.csv')
    model.reset_history_path()
    print(f"After reset, history_path: {model.history_path}")
    assert model.history_path is None
    print()


def test_output_json_and_femopt_json(monkeypatch):
    print("""
    json 出力を確認
    """)
    model = get_config_model(parent=None)
    # pyfemtetのバージョンを大きく
    monkeypatch.setattr("pyfemtet.__version__", "1.0.0")
    js = json.loads(model.output_json())
    print(f"output_json: {js}")
    assert any('femopt.optimize' in x.get('command', '') for x in js)
    js2 = json.loads(model.output_femopt_json())
    print(f"output_femopt_json: {js2}")
    assert js2[0]['command'] == "FEMOpt"
    print()


def get(qtbot, page, tag):
    tree = page.ui.treeView
    model: ConfigItemModel = get_config_model(parent=page.source_model)
    c = model.get_column_by_header_data(
        model.ColumnNames.value
    )
    r = model.get_row_by_header_data(tag.value.name)
    index = tree.model().index(r, c)
    rect = tree.visualRect(index)
    pos = rect.center()
    qtbot.mouseClick(tree.viewport(), Qt.MouseButton.LeftButton, pos=pos)
    editor = tree.findChild(type(tree.itemDelegate().createEditor(tree, QStyleOptionViewItem(), index)))
    return editor, lambda: tree.model().data(index)


def test_input_invalid_config(qtbot, page: ConfigWizardPage, monkeypatch):
    print("""
    解析実行回数に -1 を指定したら「なし」になることを確認
    """)
    tag = ConfigItemClassEnum.n_trials
    value_to_set = '-1'

    # 編集前の値を取得
    editor, getter = get(qtbot, page, tag)
    assert editor is not None
    prev_data = getter()
    print(f'{prev_data=}')

    # 編集を実行
    qtbot.keyClicks(editor, value_to_set)
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(2000)

    # 値を取得
    current_data = getter()
    print(f'{current_data=}')
    assert current_data == 'なし'
    print()


# def test_delegate_setModelData_handles_invalid(monkeypatch, qtbot: QtBot):
#     from pyfemtet_opt_gui.models.config.config import QConfigTreeViewDelegate
#     model = get_config_model(parent=None)
#     delegate = QConfigTreeViewDelegate(None)
#     delegate.set_partial_delegate_defined_model(model)
#
#     c = model.get_column_by_header_data(ConfigHeaderNames.value)
#     r = model.get_row_by_header_data(ConfigItemClassEnum.n_trials.value.name)
#     index = model.index(r, c)
#
#     class DummyEditor(QSortFilterProxyModelOfStandardItemModel):
#         def text(self):
#             return "-1"
#
#     delegate.setModelData(DummyEditor(None), model, index)
#     val1 = model.item(r, c).data(Qt.ItemDataRole.UserRole)
#     print(f"n_trials after -1 input: {val1}")
#     assert val1 is None
#
#     class DummyEditor2(QSortFilterProxyModelOfStandardItemModel):
#         def text(self):
#             return "abc"
#
#     delegate.setModelData(DummyEditor2(None), model, index)
#     val2 = model.item(r, c).data(Qt.ItemDataRole.UserRole)
#     print(f"n_trials after 'abc' input: {val2}")
#     assert val2 is None
#
#
# def test_configwizardpage_validatePage_warn(monkeypatch, qtbot: QtBot):
#     print("""
#     終了条件が未指定の場合警告が出ることを確認
#     """)
#     # page = ConfigWizardPage(parent=None)
#     # qtbot.addWidget(page)
#     # page.show()
#     # qtbot.waitExposed(page)
#     # monkeypatch.setattr(page.source_model, "is_no_finish_conditions", lambda: True)
#     #
#     # called = []
#     # # show_return_msg をモンキーパッチ
#     # monkeypatch.setattr(
#     #     cfg_mod,
#     #     "show_return_msg",
#     #     lambda return_msg, **kwargs: called.append(return_msg)
#     # )
#     #
#     # # error なので can_continue は False で返す
#     # def fake_can_continue(return_msg, **kwargs):
#     #     called.append(return_msg)
#     #     return False
#     #
#     # monkeypatch.setattr(
#     #     cfg_mod,
#     #     "can_continue",
#     #     fake_can_continue
#     # )
#     #
#     # result1 = page.validatePage()
#     # print(f"validatePage() with can_continue=False: {result1}, called={called}")
#     # assert not result1
#     #
#     # # True にする
#     # def fake_can_continue(return_msg, **kwargs):
#     #     called.append(return_msg)
#     #     return True
#     #
#     # monkeypatch.setattr(
#     #     cfg_mod,
#     #     "can_continue",
#     #     fake_can_continue
#     # )
#     #
#     # result2 = page.validatePage()
#     # print(f"validatePage() with can_continue=True: {result2}")
#     #
#     # assert result2
#     #
#     # # 通常進行時はsuper()呼び出し
#     # monkeypatch.setattr(page.source_model, "is_no_finish_conditions", lambda: False)
#     # result3 = page.validatePage()
#     # print(f"validatePage() with normal flow: {result3}")
#     print()
#
#
# def test_qconfigitemmodelforproblem_column_filter_and_history(monkeypatch):
#     model = get_config_model(parent=None)
#     proxy = QConfigItemModelForProblem(None)
#     proxy.setSourceModel(model)
#     note_col = model.get_column_by_header_data(ConfigHeaderNames.note)
#     accept_note = proxy.filterAcceptsColumn(note_col, None)
#     print(f"filterAcceptsColumn(note_col): {accept_note}")
#     assert not accept_note
#     other_col = model.get_column_by_header_data(ConfigHeaderNames.value)
#     accept_other = proxy.filterAcceptsColumn(other_col, None)
#     print(f"filterAcceptsColumn(value_col): {accept_other}")
#     assert accept_other
#     model.history_path = "dummy.csv"
#     hist_path = proxy.get_history_path()
#     print(f"Proxy get_history_path: {hist_path}")
#     assert hist_path == "dummy.csv"
#     proxy.reset_history_path()
#     print(f"After proxy.reset_history_path, model.history_path: {model.history_path}")
#     assert model.history_path is None
#
#
# def test_qconfigitemmodelforproblem_monitor_host_info(tmp_path, monkeypatch):
#     import csv
#     model = get_config_model(parent=None)
#     proxy = QConfigItemModelForProblem(None)
#     proxy.setSourceModel(model)
#     history_path = tmp_path / "hist.csv"
#     with open(history_path, "w", encoding="932", newline="\n") as f:
#         writer = csv.writer(f)
#         writer.writerow([json.dumps({"host": "localhost", "port": 12345})])
#         writer.writerow(["dummy"])
#     model.history_path = str(history_path)
#     info, msg = proxy.get_monitor_host_info()
#     print(f"monitor_host_info (exists): info={info}, msg={msg}")
#     assert info["host"] == "localhost"
#     assert info["port"] == 12345
#     assert msg == ReturnMsg.no_message
#     model.history_path = str(tmp_path / "notfound.csv")
#     info2, msg2 = proxy.get_monitor_host_info()
#     print(f"monitor_host_info (not found): info={info2}, msg={msg2}")
#     assert msg2 == ReturnMsg.Error.history_path_not_found
