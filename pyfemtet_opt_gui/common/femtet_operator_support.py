# 必要な関数のインポート
from numpy import (
    mean, max, min,
    pi, sin, cos, tan, arctan, log, sqrt, abs
)


__all__ = [
    '_femtet_operator_core',
    '_femtet_equal',
    '_femtet_not_equal',
    '_femtet_less_than',
    '_femtet_less_than_equal',
    '_femtet_greater_than',
    '_femtet_greater_than_equal',
    '_femtet_operator_and',
    '_femtet_operator_or',
    '_femtet_f_if',
    'get_femtet_builtins',
]


# Femtet の書式で書かれた変数式や拘束式を
# Python の書式に変換するための関数群
def _femtet_operator_core(b: bool):
    return -1 if b else 0


def _femtet_equal(a, b):
    return _femtet_operator_core(a == b)


def _femtet_not_equal(a, b):
    return _femtet_operator_core(a != b)


def _femtet_less_than(a, b):
    return _femtet_operator_core(a < b)


def _femtet_less_than_equal(a, b):
    return _femtet_operator_core(a <= b)


def _femtet_greater_than(a, b):
    return _femtet_operator_core(a > b)


def _femtet_greater_than_equal(a, b):
    return _femtet_operator_core(a >= b)


def _femtet_operator_and(*args):
    ret = int(args[0])
    for arg in args[1:]:
        ret = ret & int(arg)
    return ret


def _femtet_operator_or(*args):
    ret = int(args[0])
    for arg in args[1:]:
        ret = ret | int(arg)
    return ret


def _femtet_f_if(condition, if_true_or_else, if_false_or_zero):
    if not isinstance(condition, bool):
        condition = (condition != _femtet_operator_core(False))
    return if_true_or_else if condition else if_false_or_zero


# 式内の文字列に対応する
# 上記の関数群
FUNC_NAME_TO_FUNC = {
    _femtet_equal.__name__: _femtet_equal,
    _femtet_not_equal.__name__: _femtet_not_equal,
    _femtet_less_than.__name__: _femtet_less_than,
    _femtet_less_than_equal.__name__: _femtet_less_than_equal,
    _femtet_greater_than.__name__: _femtet_greater_than,
    _femtet_greater_than_equal.__name__: _femtet_greater_than_equal,
    _femtet_operator_and.__name__: _femtet_operator_and,
    _femtet_operator_or.__name__: _femtet_operator_or,
}


# 文字列中
def get_femtet_builtins(d: dict = None) -> dict:

    d = d or {}

    d.update({
        'Mean': lambda *args: float(mean(args)),
        'Max': lambda *args: float(max(args)),
        'Min': lambda *args: float(min(args)),
        'pi': pi,
        'Sin': sin,
        'Cos': cos,
        'Tan': tan,
        'Atn': arctan,
        'Log': log,
        'Sqr': sqrt,
        'Abs': abs,
        'F_IF': _femtet_f_if,
    })

    d.update(FUNC_NAME_TO_FUNC)

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
    _get_myself_code_str()
