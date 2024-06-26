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
    PARAMETER_NOT_SELECTED = '最低ひとつの変数を選択してください。'
    OBJECTIVE_NOT_SELECTED = '最低ひとつの目的関数を選択してください。'


class _ERROR(Enum):
    FEMTET_NOT_FOUND = 'Femtet プロセスが見つかりません。Femtet を起動してください。'
    FEMTET_CONNECTION_FAILED = 'Femtet との接続に失敗しました。Femtet が起動中であるか、他マクロプロセスと接続されていないか確認してください。'
    FEMTET_NO_PROJECT = '接続されている Femtet でプロジェクトが開かれていません。'  # when called from the others
    BOUND_NO_RANGE = '上限と下限が一致しています。変数の値を変更したくない場合は、use 列のチェックを外してください。'
    BOUND_INIT_OVER_UB = '初期値が上限を上回っています。'
    BOUND_INIT_UNDER_LB = '初期値が下限を下回っています。'


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

