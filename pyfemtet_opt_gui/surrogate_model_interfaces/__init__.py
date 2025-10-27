import enum
from PySide6.QtCore import QCoreApplication

__all__ = [
    'SurrogateModelNames',
]


# `no` 以外のメンバー名は pyfemtet.opt.interfaces から
# インポート可能でなければいけない
class SurrogateModelNames(enum.StrEnum):
    no = QCoreApplication.translate('pyfemtet_opt_gui.surrogate_model_interfaces', 'なし')
    # BoTorchInterface = 'BoTorchInterface'  # auto() を使うと小文字になる
    PoFBoTorchInterface = 'PoFBoTorchInterface'
