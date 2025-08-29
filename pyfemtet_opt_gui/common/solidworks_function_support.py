# 必要な関数のインポート
from numpy import (
    pi, sin, cos, tan, arcsin, arccos, arctan, log, sqrt, abs, exp,
)


__all__ = [
    'get_solidworks_builtins', 'split_unit_solidworks',
]


def split_unit_solidworks(expr_str: str) -> tuple[str, str]:
    expr_str = expr_str.strip()

    def split_core(expr_str_, unit_):    
        if expr_str_.endswith(unit_):
            return expr_str_.removesuffix(unit_), unit_
        return None

    # Solidworks で使われる単位一覧 (UI より)    
    units = ['A', 'cm', 'ft', 'in', 'uin', 'um', 'mil', 'mm', 'nm', 'deg', 'rad']

    # 'm' が存在するかどうかのチェックは
    # ほかの m で終わる単位のチェックが
    # 終わった後でなければならない
    units.extend(['m'])

    for unit in units:
        ret = split_core(expr_str, unit)
        if ret is not None:
            return ret
    return expr_str, ''


def _solidworks_iif(condition, if_true, if_false):
    assert isinstance(condition, bool), f"if_true must be bool, not {type(condition)}"
    return if_true if condition else if_false


# 文字列中
def get_solidworks_builtins(d: dict = None) -> dict:
    d = d or {}

    def sgn(x):
        if x > 0:
            return 1
        if x < 0:
            return -1
        return 0

    d.update({
        # https://help.solidworks.com/2023/Japanese/SolidWorks/sldworks/r_operators_functions_and_constants.htm?format=P&value=

        # 関数
        'sin': sin,
        'cos': cos,
        'tan': tan,
        'sec': lambda x: 1.0 / cos(x),
        'cosec': lambda x: 1.0 / sin(x),
        'cotan': lambda x: 1.0 / tan(x),
        'arcsin': arcsin,
        'arccos': arccos,
        'atn': arctan,
        'arcsec': lambda x: arccos(1.0/x),
        'arccosec': lambda x: arcsin(1.0/x),
        'arccotan': lambda x: arctan(1.0/x),
        'abs': abs,
        'exp': exp,
        'log': log,
        'sqr': sqrt,
        'int': int,  # int は Python 組み込みなので必要ないが念のため
        'sgn': sgn,

        # 定数
        'pi': pi,

        # 条件式
        'iif': _solidworks_iif,
    })

    return d
