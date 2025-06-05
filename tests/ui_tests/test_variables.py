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
    return button_to_press


def get(page, r, c):
    table = page.ui.tableView
    model = table.model()
    index = model.index(r, c)
    table.setCurrentIndex(index)
    table.edit(index)
    editor = table.focusWidget()
    return model, index, table, editor


def test_variable_page_edit_initial_value(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""initial_value を変えるテストをする""")

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
    r = 0
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.initial_value)
    model, index, table, editor = get(page, r, c)

    # 変更を実施
    qtbot.keyClicks(editor, '.5')
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(100)

    # 値が変更されている
    print(model.data(index))
    assert model.data(index) == str(.5)
    qtbot.wait(100)

    # ダイアログが出ていない
    print(called)
    assert len(called) == 0


def test_variable_page_edit_initial_value_2(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""initial_value を変えるテストをする
    
    ただし上限に違反するしたときにダイアログが出るが、
    OK を押したら変更が実行されることを確認する
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
    value = 100.
    r = 0
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.initial_value)
    model, index, table, editor = get(page, r, c)

    # 変更を実施
    qtbot.keyClicks(editor, str(value))
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(100)

    # 値が変更されている
    print(model.data(index))
    assert model.data(index) == str(value)
    qtbot.wait(100)

    # ダイアログが出ていた
    print(called)
    assert len(called) == 1 and called[0] == 'warning'


def test_variable_page_edit_initial_value_3(qtbot: QtBot, page: VariableWizardPage, monkeypatch):
    print("""initial_value を変えるテストをする
    
    ただし上限に違反するしたときにダイアログが出て、
    キャンセルを押したら編集がキャンセルされることを確認する
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
    value = -99
    r = 0
    c = page.source_model.get_column_by_header_data(
        page.source_model.ColumnNames.initial_value)
    model, index, table, editor = get(page, r, c)
    existing_text: str = model.data(index)

    # 変更を実施
    qtbot.keyClicks(editor, str(value))
    qtbot.keyClick(editor, Qt.Key.Key_Return)
    qtbot.wait(100)

    # 値が変更されていない
    print(model.data(index))
    assert model.data(index) == existing_text
    qtbot.wait(100)

    # ダイアログが出ていた
    print(called)
    assert len(called) == 1 and called[0] == 'warning-cancel'
