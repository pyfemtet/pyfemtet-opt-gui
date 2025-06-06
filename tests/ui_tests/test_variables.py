# noinspection PyUnresolvedReferences
from time import sleep
from pyfemtet_opt_gui.models.variables.var import *
from pyfemtet_opt_gui.models.variables.var import _reset_var_model

from pytestqt.qtbot import QtBot
import pytest


_dummy_data = {
    VariableColumnNames.use: [True, True, True, False],
    VariableColumnNames.name: ['x1', 'x2', 'x3', 'x4'],
    VariableColumnNames.initial_value: [0., 3.14, 'x1 + x2', 'x1 / x2'],
    VariableColumnNames.lower_bound: [-1, -1, None, None],
    VariableColumnNames.upper_bound: [1, 10., None, None],
    VariableColumnNames.step: [1, None, None, None],
    VariableColumnNames.test_value: [0., 3.14, 'x1 + x2', 'x1 / x2'],
    VariableColumnNames.note: [None, None, None, None],
}


@pytest.fixture
def page(qtbot: QtBot):
    _reset_var_model()
    page = VariableWizardPage(_dummy_data=_dummy_data)
    qtbot.addWidget(page)
    page.show()
    qtbot.waitExposed(page)

    yield page

    page.close()
    _reset_var_model()


# ダイアログを呼ぶ処理の代わり
def fake_dialog(called, kind, *_args, button_to_press=None, **_kwargs):
    button_to_press = button_to_press or QMessageBox.StandardButton.Ok
    called.append(kind)
    print('fake dialog: ', f'{kind=}', f'{button_to_press=}', _args, _kwargs)
    return button_to_press


def get(page, r, c):
    table = page.ui.tableView
    model = table.model()
    index = model.index(r, c)
    table.setCurrentIndex(index)
    table.edit(index)
    editor = table.focusWidget()
    return model, index, table, editor


# initial value の編集テスト
def test_variable_page_edit_initial_value(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== initial_value を変える =====
    警告なく編集が可能であることを確認する
    """)

    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x1 の initial_value を 0.5 に変更
    str_value = '.5'
    r = 0
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.initial_value)
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


def test_variable_page_edit_initial_value_warning(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== initial_value を変える =====
    警告が出るが編集が可能であることを確認する
    """)

    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x1 の initial_value を 100. に変更
    str_text = '100'
    r = 0
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.initial_value)
    model, index, table, editor = get(page, r, c)
    existing_text: str = model.data(index)
    print(f'{existing_text=}')

    # 変更を実施
    qtbot.keyClicks(editor, str_text)
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(50)

    # 値が変更されている
    print(model.data(index))
    assert model.data(index) == str(float(str_text))
    qtbot.wait(50)

    # ダイアログが出ていた
    print(called)
    assert len(called) == 1 and called[0] == 'warning'
    print()


def test_variable_page_edit_initial_value_warning_cancel(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== initial_value を変える =====
    警告をキャンセルすると編集がキャンセルされることを確認する
    """)

    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(
            called, 'warning-cancel', *args,
            button_to_press=QMessageBox.StandardButton.Cancel,
            **kwargs
        )
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x1 の initial_value を -99 に変更
    str_value = '-99'
    r = 0
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.initial_value)
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

    # ダイアログが出ていた
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'warning-cancel'
    print()


# lower_bound の編集テスト
def test_lower_bound(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== lower_bound の編集 =====
    警告なく編集が可能であることを確認する
    """)
    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の lower_bound を 0 に変更（既定では -1 から 0 へ: 問題ない値とする）
    str_value = '0'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.lower_bound)
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


def test_lower_bound_warning(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== lower_bound の編集 =====    
    警告が出るが編集が可能であることを確認
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の lower_bound を 5 に変更（初期値3.14なので、警告が出る（初期値以上））
    str_value = '5'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.lower_bound)
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

    # ダイアログが出ていた
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'warning'
    print()


def test_lower_bound_warning_cancel(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== lower_bound の編集 =====
    警告でキャンセルすると編集がされないことを確認
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(
            called, 'warning-cancel', *args,
            button_to_press=QMessageBox.StandardButton.Cancel,
            **kwargs
        )
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の lower_bound を 5 に変更（初期値3.14なので、警告が出る（初期値以上）。キャンセルする。）
    str_value = '5'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.lower_bound)
    model, index, table, editor = get(page, r, c)
    existing_text: str = model.data(index)
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

    # ダイアログが出ていた
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'warning-cancel'
    print()


def test_lower_bound_critical(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== lower_bound の編集 =====
    上限を超える値を設定するとエラーになることを確認
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の lower_bound を 100 に変更（上限 10 なので、エラーが出る）
    str_value = '100'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.lower_bound)
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

    # ダイアログが出ていた
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'critical'
    print()


# upper_bound の編集テスト
def test_upper_bound(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== upper_bound の編集 =====
    警告なく編集が可能であることを確認する
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の upper_bound を 5.0 に変更（既定では 10 から 5 へ: 問題ない値とする）
    str_value = '5.0'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.upper_bound)
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


def test_upper_bound_warning(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== upper_bound の編集 =====
    警告が出るが編集が可能であることを確認
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の upper_bound を 2.0 に変更（初期値3.14なので、警告が出る（初期値より下））
    str_value = '2.0'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.upper_bound)
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

    # ダイアログが出ていた
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'warning'
    print()


def test_upper_bound_warning_cancel(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== upper_bound の編集 =====
    警告でキャンセルすると編集がされないことを確認
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(
            called, 'warning-cancel', *args,
            button_to_press=QMessageBox.StandardButton.Cancel,
            **kwargs
        )
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の upper_bound を 2.0 に変更（初期値3.14なので、警告が出る（初期値より下）。キャンセルする。）
    str_value = '2.0'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.upper_bound)
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

    # ダイアログが出ていた
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'warning-cancel'
    print()


def test_upper_bound_critical(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== upper_bound の編集 =====
    下限を下回る値を設定するとエラーになることを確認
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の upper_bound を -10 に変更（下限 -1 なので、エラーが出る）
    str_value = '-10'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.upper_bound)
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

    # ダイアログが出ていた
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'critical'
    print()


# test_value の編集テスト
def test_tst_value(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== test_value の編集 =====
    編集できることを確認
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x1 の test_value を 5 に変更
    str_value = '5'
    r = 0
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.test_value)
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


def test_tst_value_critical(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== test_value の編集 =====
    他の計算式でゼロ除算エラーになるようなものはエラーになることを確認
    stderr に print_traceback しているが、正常動作
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の test_value を 0 に変更 (x4 が x1 / x2 なのでエラーになる)
    str_value = '0'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.test_value)
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

    # ダイアログが出ていた
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'critical'
    print()


# step の編集テスト
def test_step(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== step の編集 =====
    任意の数に編集できることを確認
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x2 の step を 5 に変更
    str_value = '5'
    r = 1
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.step)
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


def test_step_remove(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""
    ===== step の編集 =====
    ステップを削除できることを確認
    """)
    called = []

    monkeypatch.setattr(
        QMessageBox, 'information',
        lambda *args, **kwargs: fake_dialog(called, 'info', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'warning',
        lambda *args, **kwargs: fake_dialog(called, 'warning', *args, **kwargs)
    )
    monkeypatch.setattr(
        QMessageBox, 'critical',
        lambda *args, **kwargs: fake_dialog(called, 'critical', *args, **kwargs)
    )

    # x1 の step を ' ' に変更 ('' だとうまく動作しなかった)
    str_value = ' '
    r = 0
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.step)
    model, index, table, editor = get(page, r, c)
    existing_text: str = model.data(index)
    print(f'{existing_text=}')

    # 変更を実施
    qtbot.keyClicks(editor, str_value)
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(50)

    # 値が変更されている
    print(f'{model.data(index)=}')
    assert model.data(index) == ''
    qtbot.wait(50)

    # ダイアログが出ていない
    print(f'{called=}')
    assert len(called) == 0
    print()
