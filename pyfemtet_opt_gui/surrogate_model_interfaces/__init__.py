import enum

__all__ = [
    'SurrogateModelNames',
]


# `no` 以外のメンバー名は pyfemtet.opt.interfaces から
# インポート可能でなければいけない
class SurrogateModelNames(enum.StrEnum):
    no = 'なし'
    # BoTorchInterface = 'BoTorchInterface'  # auto() を使うと小文字になる
    PoFBoTorchInterface = 'PoFBoTorchInterface'
