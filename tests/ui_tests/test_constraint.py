from pyfemtet_opt_gui.models.constraints.model import *
from pyfemtet_opt_gui.models.constraints.model import _reset_cns_model
from pyfemtet_opt_gui.models.constraints.cns import *

from pytestqt.qtbot import QtBot
import pytest


_dummy_data = {
    ConstraintColumnNames.use: [True, True, True],
    ConstraintColumnNames.name: ['cns1', 'cns2', 'cns3'],
    ConstraintColumnNames.expr: ['x1', 'x1 + x2', 'x1 - x3'],
    ConstraintColumnNames.lb: [0, None, -3.14],
    ConstraintColumnNames.ub: [None, 1, 3.14],
    ConstraintColumnNames.note: [None, None, None],
}


@pytest.fixture
def page(qtbot: QtBot):
    _reset_cns_model()
    page = ConstraintWizardPage(_dummy_data=_dummy_data)
    qtbot.addWidget(page)
    page.show()
    qtbot.waitExposed(page)

    yield page

    page.close()
    _reset_cns_model()


# ダイアログを呼ぶ処理の代わり
def fake_dialog(called, kind, *_args, button_to_press=None, **_kwargs):
    button_to_press = button_to_press or QMessageBox.StandardButton.Ok
    called.append(kind)
    print('fake dialog: ', f'{kind=}', f'{button_to_press=}', _args, _kwargs)
    return button_to_press


# 拘束編集ダイアログを呼ぶ処理の代わり
...


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


# 削除テスト
def test_delete_constraint(qtbot: QtBot, page: ConstraintWizardPage, monkeypatch):
    print("""
    ===== 拘束を削除する =====
    警告が出て削除できることを確認
    """)

    # 状態の確認
    existing_n_rows = page.ui.tableView_cnsList.model().rowCount()
    print(f'{existing_n_rows=}')

    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch_dialog(monkeypatch, called)

    # 2 行目を選択
    r = 1
    c = page.source_model.get_column_by_header_data(
        ConstraintModel.ColumnNames.name
    )
    table = page.ui.tableView_cnsList
    model = table.model()
    index = model.index(r, c)
    table.setCurrentIndex(index)

    # 削除ボタンをクリック
    qtbot.mouseClick(page.ui.pushButton_delete, Qt.MouseButton.LeftButton)
    qtbot.wait(50)

    # 長さが減っている
    new_n_rows = page.ui.tableView_cnsList.model().rowCount()
    print(f'{new_n_rows=}')
    assert new_n_rows == existing_n_rows - 1

    # 意図通りのものが消えている
    assert model.data(model.index(0, c)) == _dummy_data[ConstraintColumnNames.name][0]
    assert model.data(model.index(1, c)) == _dummy_data[ConstraintColumnNames.name][-1]

    # ダイアログが呼ばれている
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'warning'


def test_delete_constraint_no_selection(qtbot: QtBot, page: ConstraintWizardPage, monkeypatch):
    print("""
    ===== 拘束を削除する =====
    何も選択していないとエラーになることを確認
    """)

    # 状態の確認
    existing_n_rows = page.ui.tableView_cnsList.model().rowCount()
    print(f'{existing_n_rows=}')

    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch_dialog(monkeypatch, called)

    # 削除ボタンをクリック
    qtbot.mouseClick(page.ui.pushButton_delete, Qt.MouseButton.LeftButton)
    qtbot.wait(50)

    # 長さが減っていない
    new_n_rows = page.ui.tableView_cnsList.model().rowCount()
    print(f'{new_n_rows=}')
    assert new_n_rows == existing_n_rows

    # ダイアログが呼ばれている
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'critical'


def test_delete_constraint_cancel(qtbot: QtBot, page: ConstraintWizardPage, monkeypatch):
    print("""
    ===== 拘束を削除する =====
    警告でキャンセルすると削除されないことを確認
    """)

    # 状態の確認
    existing_n_rows = page.ui.tableView_cnsList.model().rowCount()
    print(f'{existing_n_rows=}')

    # called の初期化
    called = []

    # ダイアログを呼ぶ処理の代わりを設定
    monkeypatch_dialog(monkeypatch, called, cancel_warning=True)

    # 2 行目を選択
    r = 1
    c = page.source_model.get_column_by_header_data(
        ConstraintModel.ColumnNames.name
    )
    table = page.ui.tableView_cnsList
    model = table.model()
    index = model.index(r, c)
    table.setCurrentIndex(index)

    # 削除ボタンをクリック
    qtbot.mouseClick(page.ui.pushButton_delete, Qt.MouseButton.LeftButton)
    qtbot.wait(50)

    # 長さが減っていない
    new_n_rows = page.ui.tableView_cnsList.model().rowCount()
    print(f'{new_n_rows=}')
    assert new_n_rows == existing_n_rows

    # ダイアログが呼ばれている
    print(f'{called=}')
    assert len(called) == 1 and called[0] == 'warning-cancel'
