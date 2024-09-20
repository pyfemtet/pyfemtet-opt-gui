from enum import Enum

from PySide6.QtWidgets import QMessageBox

import pyfemtet_opt_gui._p as _p


__all__ = ['ReturnCode']


class _INFO(Enum):
    SUCCEED = ''


class _WARNING(Enum):
    PID_CHANGED = '以前に接続されていた Femtet とプロセス ID が変更されています。設定に意図しない変化がないか確認してください。'
    FEMPRJ_CHANGED = '以前に開かれていた .femprj ファイルと別のファイルが開かれています。設定に意図しない変化がないか確認してください。'
    MODEL_CHANGED = '以前に開かれていた解析モデルと別名のモデルが開かれています。設定に意図しない変化がないか確認してください。'
    PARAMETRIC_OUTPUT_EMPTY = 'Femtet のパラメトリック解析 / 結果出力タブで結果を設定してください。'
    PARAMETER_EMPTY = 'Femtet で変数を設定してください。'
    FEMTET_NO_PROJECT = '接続されている Femtet でプロジェクトが開かれていません。'  # when called from launch
    PARAMETER_NOT_SELECTED = '最低でもひとつの変数を選択してください。'
    OBJECTIVE_NOT_SELECTED = '最低でもひとつの目的関数を選択してください。'
    PARAMETER_NOT_SELECTED_1 = '変数を選択してください。'


class _ERROR(Enum):
    FEMTET_NOT_FOUND = 'Femtet プロセスが見つかりません。Femtet を起動してください。'
    FEMTET_CONNECTION_FAILED = 'Femtet との接続に失敗しました。Femtet が起動中であるか、他マクロプロセスと接続されていないか確認してください。'
    FEMTET_NO_PROJECT = '接続されている Femtet でプロジェクトが開かれていません。'  # when called from the others
    BOUND_NO_RANGE = '上限と下限が一致しています。変数の値を変更したくない場合は、use 列のチェックを外してください。'
    BOUND_INIT_OVER_UB = '初期値が上限を上回っています。'
    BOUND_INIT_UNDER_LB = '初期値が下限を下回っています。'
    BOUND_LB_OVER_UB = '上下限の関係が間違っています。'
    BOUND_EMPTY = '上限か下限のいずれかを指定してください。'
    BOUND_INCOMPLETE = '上限と下限の両方を指定してください。'
    FEMTET_RECONSTRUCT_FAILED = 'Femtet でモデル再構築に失敗しました。'
    SYNTAX_ERROR_CNS_FORMULA = '式の文法が間違っています。'
    NOT_FLOAT = '数値に変換できません。'
    OLD_PYFEMTET_VERSION = 'この機能は現在のバージョンの PyFemtet ではサポートされていません。`py -m pip install pyfemtet -U` コマンドで PyFemtet をアップデートしてください。'
    UNDEFINED_FORMULA_NODE = '定義されていない変数、許可されていない関数または演算子が式に含まれています。'
    DIRECTORY_NOT_EXISTS = '存在しないフォルダのパスが指定されました。'
    NOT_AS_PYTHON_MODULE = '保存ファイル名は、以下の条件をすべて満たす必要があります。\n1. 半角の英数字及び _ 以外の文字を使わない\n2. 数字で始まらない'


class ReturnCode:

    INFO: _INFO = _INFO
    WARNING: _WARNING = _WARNING
    ERROR: _ERROR = _ERROR

    value = None


def should_stop(ret_code, parent=None) -> bool:
    if ret_code in ReturnCode.WARNING:
        _p.logger.warning(ret_code.value)
        QMessageBox.warning(parent, 'warning', ret_code.value, QMessageBox.StandardButton.Ok)
        return False

    elif ret_code in ReturnCode.ERROR:
        _p.logger.error(ret_code.value)
        QMessageBox.critical(parent, 'error', ret_code.value, QMessageBox.StandardButton.Ok)
        return True

    return False


if __name__ == '__main__':
    print(ReturnCode.ERROR.FEMTET_NOT_FOUND)
    print(ReturnCode.ERROR.FEMTET_NOT_FOUND.value)
    print(ReturnCode.ERROR.FEMTET_NOT_FOUND in ReturnCode.ERROR)
    print(ReturnCode.ERROR.FEMTET_NOT_FOUND in ReturnCode.WARNING)

