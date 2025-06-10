from PySide6.QtWidgets import QLineEdit, QStyleOptionViewItem, QComboBox
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


def get(page: ConfigWizardPage, r, c, edit=True, role=None):
    view = page.ui.treeView
    model = view.model()
    index = model.index(r, c)
    if edit:
        view.setCurrentIndex(index)
        view.edit(index)
        editor = view.focusWidget()
        return editor, lambda: model.data(index, role or Qt.ItemDataRole.DisplayRole)
    else:
        return None, lambda: model.data(index, role or Qt.ItemDataRole.DisplayRole)


def test_input_invalid_config(qtbot, page: ConfigWizardPage, monkeypatch):
    print("""
    解析実行回数に -1 を指定したら「なし」になることを確認
    """)
    value_to_set = '-1'

    # 編集前の値を取得
    editor, getter = get(page, r=0, c=1)
    assert editor is not None
    prev_data = getter()
    print(f'{prev_data=}')

    # 編集を実行
    qtbot.keyClicks(editor, value_to_set)
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(1000)

    # 値を取得
    current_data = getter()
    print(f'{current_data=}')

    assert current_data == 'なし'
    print()


# - タイムアウトに "" を入れると なし になることを確認
# - csv ファイル名に「123」と入れると、「__certify_and_get_history_path」実行時に「123.csv」が得られることを確認
# - 「並列最適化」に 2 と入れると値が 2 になり、次に 0 を入れると「なし」に戻ることを確認
# - 「最適化アルゴリズム」をコンボボックスで「PoFBoTorch」にすると、ツリー構造の子要素に「スタートアップ試行数」という要素があることを確認
# - 「シード値」に整数 42 を入力するとデータが 42 になり、「1.1」を入力すると「なし」になることを確認
# - get_surrogate_model_name の戻り値が「なし」であり、サロゲートモデルをコンボボックスで「PoFBoTorchInterface」にすると、その戻り値が「PoFBoTorchInterface」になることを確認


def get_index(page, item_enum, column_enum):
    model = page.source_model
    r = model.get_row_by_header_data(item_enum.value.name) - 1
    c = model.get_column_by_header_data(column_enum)
    return r, c


def select_combobox_item(qtbot, combobox: QComboBox, text: str):
    idx = combobox.findText(text)
    assert idx != -1, f"コンボボックスに{text}がありません"
    combobox.setCurrentIndex(idx)
    qtbot.keyClick(combobox, Qt.Key.Key_Return)


def test_timeout_empty_string_becomes_none(qtbot, page: ConfigWizardPage):
    print("""
    タイムアウトに 100 を入れると 100 になることを確認
    """)
    r, c = get_index(page, ConfigItemClassEnum.timeout, ConfigHeaderNames.value)
    editor, getter = get(page, r, c)
    assert editor is not None

    prev_data = getter()
    print(f'{prev_data=}')

    qtbot.keyClicks(editor, '100')
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(50)

    cur_data = getter()
    print(f'{cur_data=}')

    assert cur_data == '100'
    print()


def test_csv_filename_adds_csv_extension(qtbot, page: ConfigWizardPage):
    print("""
    csv ファイル名に「123」と入れると、「__certify_and_get_history_path」実行時に「123.csv」が得られることを確認
    """)
    model = page.source_model
    r, c = get_index(page, ConfigItemClassEnum.history_path, ConfigHeaderNames.value)
    editor, getter = get(page, r, c)
    assert editor is not None
    editor.setText("123")
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(100)
    # getter()はDisplayRoleの値("123")だが、certify_and_get_history_pathは.csvを付与
    path = model._ConfigItemModel__certify_and_get_history_path()
    assert path.endswith("123.csv")
    print()


def test_n_parallel_input_2_and_0(qtbot, page: ConfigWizardPage):
    print("""
    「並列最適化」に 2 と入れると値が 2 になり、次に 0 を入れると「なし」に戻ることを確認
    """)
    r, c = get_index(page, ConfigItemClassEnum.n_parallel, ConfigHeaderNames.value)
    editor, getter = get(page, r, c)
    assert editor is not None

    prev_data = getter()
    print(f'{prev_data=}')

    editor.setText("2")
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(100)

    current_data = getter()
    print(f'{current_data=}')
    assert current_data == '2'

    # 0を入れると「なし」
    editor, getter = get(page, r, c)
    editor.setText("0")
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(100)

    final_data = getter()
    print(f'{final_data=}')
    assert final_data == 'なし'

    print()


def test_algorithm_switch_to_pofbotorch_child_has_startup_trials(qtbot, page: ConfigWizardPage):
    print("""
    「最適化アルゴリズム」をコンボボックスで「PoFBoTorch」にすると、
    ツリー構造の子要素に「スタートアップ試行数」という要素があることを確認
    """)

    r, c = get_index(page, ConfigItemClassEnum.algorithm, ConfigHeaderNames.value)
    editor, getter = get(page, r, c)
    assert isinstance(editor, QComboBox)

    select_combobox_item(qtbot, editor, "PoFBoTorch")
    qtbot.wait(200)

    # 子要素を確認
    # 最適化アルゴリズムの行の0列（QStandardItemModelAsQStandardItem）
    item = page.proxy_model.sourceModel().item(r + 1, 0)
    assert item.hasChildren()
    found = False
    for row in range(item.rowCount()):
        child = item.child(row, 0)
        if child and "スタートアップ試行数" in child.text():
            found = True
            print("「スタートアップ試行数」がありました")
            break
    assert found, "PoFBoTorchの子に「スタートアップ試行数」がありません"
    print()


def test_seed_integer_and_invalid(qtbot, page: ConfigWizardPage):
    print("""
    「シード値」に整数 42 を入力するとデータが 42 になり、「1.1」を入力すると「なし」になることを確認
    """)

    r, c = get_index(page, ConfigItemClassEnum.seed, ConfigHeaderNames.value)
    editor, getter = get(page, r, c)
    assert editor is not None

    prev_data = getter()
    print(f'{prev_data=}')

    # 42を入力
    editor.setText("42")
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(100)

    current_data = getter()
    print(f'{current_data=}')
    assert current_data == '42'

    # 1.1を入力
    editor, getter = get(page, r, c)
    editor.setText("1.1")
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(100)

    final_data = getter()
    print(f'{final_data=}')
    assert final_data == 'なし'

    print()


def test_surrogate_model_name(qtbot, page: ConfigWizardPage):
    print("""
    get_surrogate_model_name の戻り値が「なし」であり、
    サロゲートモデルをコンボボックスで「PoFBoTorchInterface」にすると、
    その戻り値が「PoFBoTorchInterface」になることを確認
    """)
    # 初期値は SurrogateModelNames.no
    model = page.source_model
    assert model.get_surrogate_model_name() == SurrogateModelNames.no

    r, c = get_index(page, ConfigItemClassEnum.surrogate_model_name, ConfigHeaderNames.value)
    editor, getter = get(page, r, c)
    assert isinstance(editor, QComboBox)

    prev_data = getter()
    print(f'{prev_data=}')
    print(f' should equals to {model.get_surrogate_model_name()=}')

    select_combobox_item(qtbot, editor, SurrogateModelNames.PoFBoTorchInterface.value)
    qtbot.wait(100)

    current_data = getter()
    print(f'{current_data=}')
    print(f' should equals to {model.get_surrogate_model_name()=}')

    assert current_data == SurrogateModelNames.PoFBoTorchInterface.value
    assert model.get_surrogate_model_name() == SurrogateModelNames.PoFBoTorchInterface
