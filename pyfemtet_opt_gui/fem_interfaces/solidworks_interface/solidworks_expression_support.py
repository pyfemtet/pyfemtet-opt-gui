# 必要な関数のインポート
from numpy import (
    pi, sin, cos, tan, arcsin, arccos, arctan, log, sqrt, abs, exp,
)


__all__ = [
    'get_fem_builtins', 'split_unit_solidworks',
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
def get_fem_builtins(d: dict = None) -> dict:
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


def _get_myself_code_str():
    import ast
    from locale import getencoding

    try:
        with open(__file__, encoding='utf-8') as f:
            src = f.read()
    except UnicodeDecodeError:
        with open(__file__, encoding=getencoding()) as f:
            src = f.read()

    tree = ast.parse(src, filename=__file__)

    dst = []
    for node in tree.body:
        should_skip = False

        # __all__ への代入であればスキップ
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    if t.id == '__all__':
                        should_skip = True

        # この関数ならスキップ
        if isinstance(node, ast.FunctionDef):
            if node.name == '_get_myself_code_str':
                should_skip = True

        # __main__ 節なら削除
        if isinstance(node, ast.If):
            should_skip_partial = []

            # 比較ならば
            if isinstance(node.test, ast.Compare):
                left = node.test.left
                comparators = node.test.comparators

                # 左辺が __name__ ならば
                should_skip_partial.append(False)
                if isinstance(left, ast.Name):
                    if left.id == '__name__':
                        should_skip_partial[-1] = True

                # == '__main__' ならば
                should_skip_partial.append(False)
                if len(comparators) == 1:
                    comparator = comparators[0]
                    if isinstance(comparator, ast.Constant):
                        if comparator.value == '__main__':
                            should_skip_partial[-1] = True

                # 上記両方とも満たすならば削除
                should_skip = all(should_skip_partial)

        if not should_skip:
            dst.append(node)

    tree.body = dst
    code_str = ast.unparse(tree)

    return code_str


if __name__ == '__main__':
    print(_get_myself_code_str())
