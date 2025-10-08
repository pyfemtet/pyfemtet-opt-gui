from pyfemtet_opt_gui.common.qt_util import *

import pyfemtet_opt_gui.fem_interfaces  # noqa  # expression_processor の import error の暫定対策
from pyfemtet_opt_gui.models.constraints.model import *
from pyfemtet_opt_gui.models.constraints.model import _reset_cns_model
import pyfemtet_opt_gui.models.constraints.cns as cns_mod  # for monkey patch
from pyfemtet_opt_gui.models.constraints.cns import *
from pyfemtet_opt_gui.models.constraints.cns_dialog import ConstraintEditorDialog
import pyfemtet_opt_gui.models.constraints.cns_dialog as cns_dlg_mod  # for monkey patch
from pyfemtet_opt_gui.models.variables.var import (
    VariableItemModel,
    VariableColumnNames,
    get_var_model,
    _reset_var_model,
)

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


_dummy_data_var = {
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
    _reset_cns_model()
    page = ConstraintWizardPage(_dummy_data=_dummy_data)
    qtbot.addWidget(page)
    page.show()
    qtbot.waitExposed(page)

    _start_debugging()
    yield page
    _end_debugging()

    page.close()
    _reset_cns_model()
    _reset_var_model()


@pytest.fixture
def var_model(page: ConstraintWizardPage):
    _reset_var_model()
    model = get_var_model(parent=page.parent(), _dummy_data=_dummy_data_var)

    yield model

    _reset_var_model()


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


# 既存の _dummy_data, monkeypatch_dialog, page フィクスチャなどはそのまま利用

# --- テスト1: 追加ボタンでダイアログ→サンプルConstraint追加 ---
def test_add_constraint_opens_dialog_and_adds(
        qtbot: QtBot,
        page: ConstraintWizardPage,
        monkeypatch,
        var_model: VariableItemModel,
):
    print("""
    pushButton_addを押すと編集ダイアログが開き、サンプルConstraintを返すようにモンキーパッチすると
    ConstraintModelにデータが追加されることを確認
    """)

    # 追加前の件数
    model = page.source_model
    before_count = len(model.get_constraint_names())

    # 編集ダイアログをモンキーパッチ
    class FakeDialog:
        def __init__(self, *a, **kw):
            # サンプルConstraintを追加
            constraint = Constraint(var_model)
            constraint.name = "sample_added"
            constraint.expression = "x1 + x2"
            constraint.lb = 0
            constraint.ub = 5
            model.set_constraint(constraint)
            self._accepted = True

        def setModal(self, val): pass

        def show(self): self._accepted = True

        def close(self):pass

        def exec(self): return self._accepted

        def accept(self): self._accepted = True

        def reject(self): self._accepted = False

    monkeypatch.setattr(cns_mod, 'ConstraintEditorDialog', FakeDialog)

    # ダイアログが開いたかのフラグ
    # 実際はFakeDialog.show()なのでOK

    before_names = model.get_constraint_names()
    print(f'{before_names=}')

    # 追加ボタン押下
    qtbot.mouseClick(page.ui.pushButton_add, Qt.MouseButton.LeftButton)
    qtbot.wait(50)

    # 件数増加を確認
    after_names = model.get_constraint_names()
    print(f'{after_names=}')
    assert len(after_names) == before_count + 1
    assert "sample_added" in after_names
    print()


# --- テスト2: 編集ボタンで選択中Constraint名がダイアログに渡ることを確認 ---
def test_edit_button_opens_editor_with_selected_constraint(qtbot: QtBot, page: ConstraintWizardPage, monkeypatch):
    print("""
    ダミーデータを選択し編集ボタンを押すと、選択中のデータ名でダイアログ（Fake）に渡されることを確認
    """)

    # 編集ダイアログをモンキーパッチ
    called = dict(name=None)

    class FakeDialog:
        def __init__(self, parent=None, existing_constraint_name=None, **kwargs):
            called['name'] = existing_constraint_name

        def setModal(self, val): pass

        def show(self): pass

        def close(self): pass

    monkeypatch.setattr(cns_mod, 'ConstraintEditorDialog', FakeDialog)

    # 1行目(0-indexed)を選択
    r = 0
    c = page.source_model.get_column_by_header_data(ConstraintModel.ColumnNames.name)
    proxy_index = page.proxy_model.index(r, c)
    page.view.setCurrentIndex(proxy_index)

    # 編集ボタン押下
    qtbot.mouseClick(page.ui.pushButton_edit, Qt.MouseButton.LeftButton)
    qtbot.wait(50)

    # 編集ダイアログに正しい名前が渡されたか
    expected_name = _dummy_data[ConstraintColumnNames.name][r]
    assert called['name'] == expected_name
    print()


# --- テスト3: 編集ダイアログで上限0/下限1→エラー(下限>上限) ---
def test_editor_lb_gt_ub_error(qtbot: QtBot, monkeypatch):
    print("""
    編集ダイアログで上限0/下限1を入れるとエラーになることを確認
    """)

    _reset_cns_model()
    dialog = ConstraintEditorDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)

    # 名前・式・上下限入力
    dialog.ui.lineEdit_name.setText("test_lb_gt_ub")
    dialog.ui.plainTextEdit_cnsFormula.setPlainText("x1")
    dialog.ui.lineEdit_lb.setText("1")
    dialog.ui.lineEdit_ub.setText("0")

    # 初期化
    error_msgs = []

    # show_return_msg をモンキーパッチ
    monkeypatch.setattr(
        cns_dlg_mod,
        "show_return_msg",
        lambda return_msg, **kwargs: error_msgs.append(return_msg)
    )

    # error なので can_continue は False で返す
    def fake_can_continue(return_msg, **kwargs):
        error_msgs.append(return_msg)
        return False

    monkeypatch.setattr(
        cns_dlg_mod,
        "can_continue",
        fake_can_continue
    )

    # OK押下
    dialog.accept()

    # エラーが出ていること
    print(error_msgs)
    assert len(error_msgs) == 1
    assert error_msgs[0] == ReturnMsg.Error.inconsistent_lb_ub
    print()


# --- テスト4: 編集ダイアログで上限に文字式→エラーで入力取り消し ---
def test_editor_ub_not_number_error(qtbot: QtBot, monkeypatch):
    print("""
    編集ダイアログで上限に文字列式を入力するとエラーダイアログが出て入力が取り消されることを確認
    """)

    # 初期化
    error_msgs = []

    # show_return_msg をモンキーパッチ
    monkeypatch.setattr(
        cns_dlg_mod,
        "show_return_msg",
        lambda return_msg, **kwargs: error_msgs.append(return_msg)
    )

    # error なので can_continue は False で返す
    def fake_can_continue(return_msg, **kwargs):
        error_msgs.append(return_msg)
        return False

    monkeypatch.setattr(
        cns_dlg_mod,
        "can_continue",
        fake_can_continue
    )

    _reset_cns_model()
    dialog = ConstraintEditorDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)

    dialog.ui.lineEdit_name.setText("test_ub_not_number")
    dialog.ui.plainTextEdit_cnsFormula.setPlainText("x1")
    dialog.ui.lineEdit_lb.setText("0")
    dialog.ui.lineEdit_ub.setText("not_a_number")

    # OK押下
    dialog.accept()

    # エラーが出ていること
    print(error_msgs)
    assert len(error_msgs) == 1
    assert error_msgs[0] == ReturnMsg.Error.not_a_pure_number
    print()


# --- テスト5: パラメータ選択→「選択中の変数を入力」で式に変数名が入力される ---
def test_editor_insert_selected_variable(
        qtbot: QtBot,
        page,
        var_model,
        monkeypatch,
):
    print("""
    編集ダイアログでパラメータを選択し「選択中の変数を入力」ボタンで式エディタに変数が入力される
    """)

    # cns_dialog の get_var_model を
    # fixture を返すものに交換
    monkeypatch.setattr(
        cns_dlg_mod,
        'get_var_model',
        lambda *a, **kw: var_model
    )

    # cns_dialog の get_cns_model を
    # fixture を返すものに交換
    monkeypatch.setattr(
        cns_dlg_mod,
        'get_cns_model',
        lambda *a, **kw: page.source_model
    )

    dialog = ConstraintEditorDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)

    # 変数テーブルの最初のパラメータを選択
    table = dialog.ui.tableView_prmsOnCns
    model = table.model()
    index = model.index(0, 0)  # 1行目1列目
    table.setCurrentIndex(index)

    # plainTextEdit_cnsFormula をクリア
    dialog.ui.plainTextEdit_cnsFormula.setPlainText("")

    # エディタのクリアを確認
    cleared_text = dialog.ui.plainTextEdit_cnsFormula.toPlainText()
    print(f'{cleared_text=}')

    # 「選択中の変数を入力」ボタン押下
    qtbot.mouseClick(dialog.ui.pushButton_input_var, Qt.MouseButton.LeftButton)
    qtbot.wait(50)

    # エディタに変数名が入力されたか
    text = dialog.ui.plainTextEdit_cnsFormula.toPlainText()
    # 最初の変数名はモデル依存だが、空でなければOK
    print(f'{text=}')
    assert text == ' x1 '
    print()


# --- テスト6: 計算結果が上限を超えると警告ダイアログが出る ---
def test_editor_expression_exceeds_upper_warn(
        qtbot: QtBot,
        page,
        var_model,
        monkeypatch,
):
    print("""
    文字式の計算結果が上限を超える場合にOKで警告ダイアログが出ることを確認
    """)

    # cns_dialog の get_var_model を
    # fixture を返すものに交換
    monkeypatch.setattr(
        cns_dlg_mod,
        'get_var_model',
        lambda *a, **kw: var_model
    )

    # cns_dialog の get_cns_model を
    # fixture を返すものに交換
    monkeypatch.setattr(
        cns_dlg_mod,
        'get_cns_model',
        lambda *a, **kw: page.source_model
    )

    dialog = ConstraintEditorDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)

    dialog.ui.lineEdit_name.setText("test_warn")
    dialog.ui.plainTextEdit_cnsFormula.setPlainText("100")  # 計算値100
    dialog.ui.lineEdit_lb.setText("0")
    dialog.ui.lineEdit_ub.setText("50")  # 上限50

    # 警告ダイアログを捕捉
    called = []

    def fake_can_continue(return_msg, **kwargs):
        called.append(return_msg)
        return True

    monkeypatch.setattr(
        cns_dlg_mod,
        "can_continue",
        fake_can_continue
    )

    # OK押下
    dialog.accept()
    print(f'{called=}')
    assert len(called) == 1
    assert called[0] == ReturnMsg.Warn.inconsistent_value_bounds
    print()

    print(f'{dialog.isHidden()=}')
    assert dialog.isHidden() is True


# --- テスト7: 計算結果が上限を超え、警告ダイアログでキャンセルするとダイアログが閉じない ---
def test_editor_expression_exceeds_upper_warn_cancel(
        qtbot: QtBot,
        page,
        var_model,
        monkeypatch,
):
    print("""
    計算結果が上限を超え警告、キャンセルでダイアログが閉じないことを確認
    """)

    # cns_dialog の get_var_model を
    # fixture を返すものに交換
    monkeypatch.setattr(
        cns_dlg_mod,
        'get_var_model',
        lambda *a, **kw: var_model
    )

    # cns_dialog の get_cns_model を
    # fixture を返すものに交換
    monkeypatch.setattr(
        cns_dlg_mod,
        'get_cns_model',
        lambda *a, **kw: page.source_model
    )

    dialog = ConstraintEditorDialog()
    qtbot.addWidget(dialog)
    dialog.show()
    qtbot.waitExposed(dialog)

    dialog.ui.lineEdit_name.setText("test_warn")
    dialog.ui.plainTextEdit_cnsFormula.setPlainText("100")  # 計算値100
    dialog.ui.lineEdit_lb.setText("0")
    dialog.ui.lineEdit_ub.setText("50")  # 上限50

    # 警告ダイアログを捕捉
    called = []

    def fake_can_continue(return_msg, **kwargs):
        called.append(return_msg)
        return False

    monkeypatch.setattr(
        cns_dlg_mod,
        "can_continue",
        fake_can_continue
    )

    # OK押下
    dialog.accept()
    print(f'{called=}')
    assert len(called) == 1
    assert called[0] == ReturnMsg.Warn.inconsistent_value_bounds
    print()

    print(f'{dialog.isHidden()=}')  # False
    assert dialog.isHidden() is False
