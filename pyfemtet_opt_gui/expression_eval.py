import ast
import statistics  # mean

from typing import Callable
from pyfemtet.opt import AbstractOptimizer


__all__ = ['create_formula', 'DummyOptimizer', 'ExpressionEvalError', 'extract_variables']


class ExpressionEvalError(Exception):
    pass


class DummyOptimizer:

    def __init__(self, prm: dict):
        self.prm = prm

    def get_parameter(self):
        return self.prm


class CFemtet:
    pass


class FormulaEvaluator(ast.NodeVisitor):
    """AST Node Visitor to safely evaluate mathematical expressions."""

    def __init__(self, variables: dict):
        self.variables = variables

    def visit_BinOp(self, node):
        """Visit binary operations like addition, subtraction, etc."""
        left = self.visit(node.left)
        right = self.visit(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        elif isinstance(node.op, ast.Sub):
            return left - right
        elif isinstance(node.op, ast.Mult):
            return left * right
        elif isinstance(node.op, ast.Div):
            return left / right
        elif isinstance(node.op, ast.Mod):
            return left % right
        elif isinstance(node.op, ast.Pow):
            return left ** right
        elif isinstance(node.op, ast.FloorDiv):
            return left // right
        else:
            raise ExpressionEvalError(f"Unsupported binary operator: {ast.dump(node.op)}")

    def visit_Num(self, node):
        """Visit numbers."""
        return node.n

    def visit_Constant(self, node):
        """Visit constants (Python 3.8+ uses `Constant` instead of `Num`)."""
        if isinstance(node.value, (int, float)):
            return node.value
        raise ExpressionEvalError(f"Unsupported constant type: {type(node.value)}")

    def visit_Name(self, node):
        """Visit variable names."""
        if node.id in self.variables:
            return self.variables[node.id]
        raise ExpressionEvalError(f"Undefined variable: {node.id}")

    def visit_Call(self, node):
        """Visit function calls like max(), min(), mean()"""
        func_name = node.func.id
        if func_name == 'max':
            args = [self.visit(arg) for arg in node.args]
            return max(args)
        elif func_name == 'min':
            args = [self.visit(arg) for arg in node.args]
            return min(args)
        elif func_name == 'mean':
            args = [self.visit(arg) for arg in node.args]
            return statistics.mean(args)
        else:
            raise ExpressionEvalError(f"Unsupported function: {func_name}")

    def generic_visit(self, node):
        """Raise an error for unsupported nodes."""
        raise ExpressionEvalError(f"Unsupported operation: {ast.dump(node)}")


class VariableExtractor(ast.NodeVisitor):
    def __init__(self):
        self.variables = set()
        self.functions = set()

    def visit_Name(self, node):
        # 変数名が識別子の場合のみセットに追加
        if isinstance(node.ctx, ast.Load):  # 読み込みの場合
            self.variables.add(node.id)
        self.generic_visit(node)  # 他のノードも訪問

    def visit_Call(self, node):
        """Visit function calls like max(), min(), mean()"""
        func_name = node.func.id
        self.functions.add(func_name)
        self.generic_visit(node)


def extract_variables(expression):
    tree = ast.parse(expression, mode='eval')  # 式をASTに変換
    extractor = VariableExtractor()
    extractor.visit(tree.body)  # ASTノードを訪問
    return extractor.variables - extractor.functions


def create_formula(expression: str, var_names: list[str] = None) -> Callable[[CFemtet, AbstractOptimizer], float]:
    """Create formula from expression string using AST for safe evaluation.

    Raises:
        SyntaxError: If the expression cannot be parsed
        ValueError: If the expression cannot be evaluated as a formula.

    Returns:
        Callable: A function that receives a DummyOptimizer object and returns a float.
    """

    # Parse the expression into an AST
    tree = ast.parse(expression, mode='eval')

    # only check undefined variables
    if var_names is not None:
        local_vars = {k: 1 for k in var_names}
        evaluator = FormulaEvaluator(local_vars)

        try:
            evaluator.visit(tree.body)
        except ZeroDivisionError:
            pass

    # Ensure the parsed tree only contains safe nodes
    def fun(Femtet: CFemtet, opt: AbstractOptimizer) -> float:
        # Extract variables from the optimizer's params
        # local_vars = {k: opt.get_parameter()[k] for k in opt.get_parameter()}
        local_vars = opt.get_parameter()

        # Use the FormulaEvaluator to safely evaluate the expression
        evaluator = FormulaEvaluator(local_vars)

        try:
            result = evaluator.visit(tree.body)  # Evaluate the expression
            if not isinstance(result, (int, float)):
                raise ValueError("Expression did not evaluate to a float or int.")
            return result
        except Exception as e:
            raise RuntimeError(f"Failed to evaluate expression: {e}")

    return fun


def test():

    opt = DummyOptimizer(dict(a=1., b=2., c=3.))

    # Test example:
    formula = create_formula('(a + b) / c')
    result = formula(None, opt)
    print(f"Result: {result}")

    # Test example:
    try:
        formula = create_formula('(a + b / c')  # syntax error
    except SyntaxError as e:
        print(e)

    # Test example:
    formula = create_formula('d + b / c')  # not defined
    try:
        result = formula(None, opt)
    except RuntimeError as e:
        print(e)

    # Test example:
    formula = create_formula('(a + b) ** c')
    result = formula(None, opt)
    print(f"Result: {result}")

    # Test example:
    formula = create_formula('(a + b) // c')
    result = formula(None, opt)
    print(f"Result: {result}")

    # Test example:
    formula = create_formula('mean(a, b, c)')
    result = formula(None, opt)
    print(f"Result: {result}")

    # Test example:
    formula = create_formula('max(a, b, c)')
    result = formula(None, opt)
    print(f"Result: {result}")

    # Test example:
    formula = create_formula('min(a, b, c)')
    result = formula(None, opt)
    print(f"Result: {result}")

    # Test example:
    try:
        formula = create_formula('d + b / c', ['d', 'b'])  # not defined
    except ExpressionEvalError as e:
        print(e)

    # Test example:
    try:
        formula = create_formula('d + b / some(c)', ['d', 'b', 'c'])  # not defined
    except ExpressionEvalError as e:
        print(e)


if __name__ == '__main__':
    test()
