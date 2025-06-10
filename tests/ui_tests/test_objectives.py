# noinspection PyUnresolvedReferences
from time import sleep
from femtetutils import util
from pyfemtet_opt_gui.models.objectives.obj import *
from pyfemtet_opt_gui.models.objectives.obj import _reset_obj_model
import pyfemtet_opt_gui.fem_interfaces as fi

from pytestqt.qtbot import QtBot
import pytest

from tests import get_test_femprj_path
from tests.ui_tests.test_variables import fem


_dummy_data = {
    ObjectiveColumnNames.use: [True, True, True],
    ObjectiveColumnNames.name: ['y1', 'y2', 'y3'],
    ObjectiveColumnNames.direction: [ObjectiveDirection.minimize, ObjectiveDirection.maximize, ObjectiveDirection.specific_value],
    ObjectiveColumnNames.target_value: [0., 0., 10.],
    ObjectiveColumnNames.note: [None, None, None],
}


@pytest.fixture
def page(qtbot: QtBot):
    _reset_obj_model()
    page = ObjectiveWizardPage(_dummy_data=_dummy_data)
    qtbot.addWidget(page)
    page.show()
    qtbot.waitExposed(page)

    yield page

    page.close()
    _reset_obj_model()


# ダイアログを呼ぶ処理の代わり
def fake_dialog(called, kind, *_args, button_to_press=None, **_kwargs):
    button_to_press = button_to_press or QMessageBox.StandardButton.Ok
    called.append(kind)
    print('fake dialog: ', f'{kind=}', f'{button_to_press=}', _args, _kwargs)
    return button_to_press


def monkeypatch_dialog(monkeypatch, called, cancel_warning=False):
    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    if cancel_warning:
        monkeypatch.setattr(
            QMessageBox, 'warning',
            lambda *args, **kwargs: fake_dialog(
                called, 'warning-cancel', *args,
                button_to_press=QMessageBox.StandardButton.Cancel, **kwargs)
        )
    else:
        monkeypatch.setattr(
            QMessageBox, 'warning',
            lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
        )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )


def get(page, r, c, edit=True):
    table = page.ui.tableView
    model = table.model()
    index = model.index(r, c)
    if edit:
        table.setCurrentIndex(index)
        table.edit(index)
        editor = table.focusWidget()
        return model, index, table, editor
    else:
        return model, index, table, None


def test_edit_target_value(qtbot: QtBot, page: ObjectiveWizardPage, monkeypatch):
    print("""
    ===== target value を変える =====
    aim for のとき、target value が変更できる
    """)

    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch_dialog(monkeypatch, called)

    # y3 の target value を 0.5 に変更
    str_value = '0.5'
    r = 2
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.target_value)
    model, index, table, editor = get(page, r, c)
    existing_text: str = model.data(index)
    print(f'{existing_text=}')

    # 変更を実施
    qtbot.keyClicks(editor, str_value)
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(50)

    # 値が変更されている
    print(f'{model.data(index)=}')
    assert model.data(index) == str(float(str_value))
    qtbot.wait(50)

    # ダイアログが出ていない
    print(f'{called=}')
    assert len(called) == 0
    print()


def test_cannot_edit_target_value(qtbot: QtBot, page: ObjectiveWizardPage, monkeypatch):
    print("""
    ===== target value を変える =====
    maximize のとき、target value が変更できない
    """)

    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch_dialog(monkeypatch, called)

    # y2 の target value を 0.5 に変更
    str_value = '0.5'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.target_value)
    model, index, table, editor = get(page, r, c)
    existing_text: str = model.data(index)
    print(f'{existing_text=}')

    # 変更を実施
    qtbot.keyClicks(editor, str_value)
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(50)

    # 値が変更されていない
    print(f'{model.data(index)=}')
    assert model.data(index) == existing_text
    qtbot.wait(50)

    # ダイアログが出ていない
    print(f'{called=}')
    assert len(called) == 0
    print()


def test_change_edit_target_value(qtbot: QtBot, page: ObjectiveWizardPage, monkeypatch):
    print("""
    ===== target value を変える =====
    maximize を target value にすると
    値が変更できる
    """)

    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch_dialog(monkeypatch, called)

    # y2 の direction を aim for に変更
    str_value = ObjectiveDirection.specific_value
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.direction)
    model, index, table, editor = get(page, r, c)
    existing_text: str = model.data(index)
    print(f'{existing_text=}')

    # 変更を実施
    qtbot.keyClicks(editor, str_value)
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(50)

    # y2 の target value を 0.5 に変更
    str_value = '0.5'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.target_value)
    model, index, table, editor = get(page, r, c)
    existing_text: str = model.data(index)
    print(f'{existing_text=}')

    # 変更を実施
    qtbot.keyClicks(editor, str_value)
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(50)

    # 値が変更されている
    print(f'{model.data(index)=}')
    assert model.data(index) == str_value
    qtbot.wait(50)

    # ダイアログが出ていない
    print(f'{called=}')
    assert len(called) == 0
    print()


# load femtet のテスト
def test_load_femtet(qtbot: QtBot, page: ObjectiveWizardPage, monkeypatch, fem):
    print("""
    ===== load from femtet の編集 =====
    Femtet からロードしてエラーにならないことを確認
    """)
    called = []

    monkeypatch_dialog(monkeypatch, called)

    qtbot.mouseClick(page.ui.pushButton, Qt.MouseButton.LeftButton)
    qtbot.wait(50)

    names = [
        '0: 定常解析\n温度[deg]\n最大値\n発熱部品',
        '0: 定常解析\n速度ポテンシャル[m2/s]\n最大値\n流路',
    ]

    for r in range(page.ui.tableView.model().rowCount()):

        # name
        key = page.source_model.ColumnNames.name
        c = page.source_model.get_column_by_header_data(key)
        model, index, table, editor = get(page, r, c, False)
        existing_text: str | None = model.data(index)
        print(key, f'{existing_text=}')
        assert existing_text == names[r]

    print()
