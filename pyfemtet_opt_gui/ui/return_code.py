from enum import Enum


__all__ = ['ReturnCode']





class _INFO(Enum):
    SUCCEED = ''


class _WARNING(Enum):
    PID_CHANGED = '以前に接続されていた Femtet とプロセス ID が変更されています。設定に意図しない変化がないか確認してください。'
    FEMPRJ_CHANGED = '以前に開かれていた .femprj ファイルと別のファイルが開かれています。設定に意図しない変化がないか確認してください。'
    MODEL_CHANGED = '以前に開かれていた解析モデルと別名のモデルが開かれています。設定に意図しない変化がないか確認してください。'
    PARAMETRIC_OUTPUT_EMPTY = 'Femtet のパラメトリック解析 / 結果出力タブで結果を設定してください。'
    PARAMETER_EMPTY = 'Femtet で変数を設定してください。'


class _ERROR(Enum):
    FEMTET_NOT_FOUND = 'Femtet プロセスが見つかりません。Femtet を起動してください。'
    FEMTET_CONNECTION_FAILED = 'Femtet との接続に失敗しました。Femtet が起動中であるか、他マクロプロセスと接続されていないか確認してください。'
    FEMTET_NO_PROJECT = '接続されている Femtet でプロジェクトが開かれていません。'


class ReturnCode:

    INFO: _INFO = _INFO
    WARNING: _WARNING = _WARNING
    ERROR: _ERROR = _ERROR

    value = None


if __name__ == '__main__':
    print(ReturnCode.ERROR.FEMTET_NOT_FOUND)
    print(ReturnCode.ERROR.FEMTET_NOT_FOUND.value)
    print(ReturnCode.ERROR.FEMTET_NOT_FOUND in ReturnCode.ERROR)
    print(ReturnCode.ERROR.FEMTET_NOT_FOUND in ReturnCode.WARNING)

