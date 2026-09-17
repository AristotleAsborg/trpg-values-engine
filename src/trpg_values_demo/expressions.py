"""对外部配置里写的公式做安全求值。

只支持算术 / 比较 / 布尔运算、括号、三元表达式，以及引用已命名的变量
（属性名、技能名、先前算出的派生值）。函数调用、属性访问、下标、推导式、
导入等一律拒绝——配置文件来自脚本之外，不能让它获得执行能力。
"""

from __future__ import annotations

import ast
from typing import Any, Mapping

__all__ = ["ExpressionError", "evaluate"]


class ExpressionError(ValueError):
    """公式非法，或者求值失败。"""


_BIN_OPS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
}

_CMP_OPS = {
    ast.Eq: lambda a, b: a == b,
    ast.NotEq: lambda a, b: a != b,
    ast.Lt: lambda a, b: a < b,
    ast.LtE: lambda a, b: a <= b,
    ast.Gt: lambda a, b: a > b,
    ast.GtE: lambda a, b: a >= b,
}


def evaluate(expression: str, variables: Mapping[str, Any] | None = None) -> Any:
    """求值 ``expression``，可用变量由 ``variables`` 提供。

    变量名与公式全部来自外部规则配置，本模块不认识任何具体的规则系统；
    公式示例见 README 与 ``rules/example_rules.json``（放在包外，
    这样"包源码里没有硬编码规则"这条约束可以被脚本机械核对）。
    """
    if not isinstance(expression, str):
        raise ExpressionError(f"公式必须是字符串，得到 {type(expression).__name__}")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"公式语法错误: {expression!r}: {exc.msg}") from exc

    scope: dict[str, Any] = dict(variables or {})
    try:
        return _eval(tree, scope)
    except ExpressionError:
        raise
    except ZeroDivisionError as exc:
        raise ExpressionError(f"公式出现除零: {expression!r}") from exc
    except (TypeError, ValueError) as exc:
        raise ExpressionError(f"公式求值失败: {expression!r}: {exc}") from exc


def _eval(node: ast.AST, scope: dict[str, Any]) -> Any:
    if isinstance(node, ast.Expression):
        return _eval(node.body, scope)

    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float, bool)):
            return node.value
        raise ExpressionError(f"公式中不允许的常量: {node.value!r}")

    if isinstance(node, ast.Name):
        if node.id in scope:
            return scope[node.id]
        raise ExpressionError(f"公式引用了未知变量: {node.id!r}")

    if isinstance(node, ast.BinOp):
        op = _BIN_OPS.get(type(node.op))
        if op is None:
            raise ExpressionError(f"公式中不允许的二元运算符: {type(node.op).__name__}")
        return op(_eval(node.left, scope), _eval(node.right, scope))

    if isinstance(node, ast.UnaryOp):
        operand = _eval(node.operand, scope)
        if isinstance(node.op, ast.USub):
            return -operand
        if isinstance(node.op, ast.UAdd):
            return +operand
        if isinstance(node.op, ast.Not):
            return not operand
        raise ExpressionError(f"公式中不允许的一元运算符: {type(node.op).__name__}")

    if isinstance(node, ast.Compare):
        left = _eval(node.left, scope)
        for op, comparator in zip(node.ops, node.comparators):
            compare = _CMP_OPS.get(type(op))
            if compare is None:
                raise ExpressionError(f"公式中不允许的比较运算符: {type(op).__name__}")
            right = _eval(comparator, scope)
            if not compare(left, right):
                return False
            left = right
        return True

    if isinstance(node, ast.BoolOp):
        if isinstance(node.op, ast.And):
            result: Any = True
            for value in node.values:
                result = _eval(value, scope)
                if not result:
                    return result
            return result
        if isinstance(node.op, ast.Or):
            result = False
            for value in node.values:
                result = _eval(value, scope)
                if result:
                    return result
            return result
        raise ExpressionError(f"公式中不允许的布尔运算符: {type(node.op).__name__}")

    if isinstance(node, ast.IfExp):
        if _eval(node.test, scope):
            return _eval(node.body, scope)
        return _eval(node.orelse, scope)

    raise ExpressionError(f"公式中不允许的语法: {type(node).__name__}")
