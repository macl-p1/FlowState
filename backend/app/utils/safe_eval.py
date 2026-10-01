"""Safe expression evaluator using Python AST.

Replaces eval() for condition node expressions. Only allows:
- Comparisons (==, !=, <, >, <=, >=)
- Boolean operators (and, or, not)
- Arithmetic (+, -, *, /, %, **)
- Literals (str, int, float, bool, None)
- Variable name lookups from a context dict
- Attribute access for dict key lookups (e.g., result.status)
- Function calls to whitelisted builtins (len, str, int, float, bool)

Blocks: imports, exec, attribute access to dunder methods, arbitrary code execution.
"""
from __future__ import annotations

import ast
import operator
import typing as t


# Whitelisted binary operators
_BIN_OPS: dict[type, t.Callable] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
}

# Whitelisted unary operators
_UNARY_OPS: dict[type, t.Callable] = {
    ast.Not: operator.not_,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

# Whitelisted comparison operators
_CMP_OPS: dict[type, t.Callable] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Is: operator.is_,
    ast.IsNot: operator.is_not,
    ast.In: lambda a, b: a in b,
    ast.NotIn: lambda a, b: a not in b,
}

# Whitelisted boolean operators
_BOOL_OPS: dict[type, t.Callable] = {
    ast.And: all,
    ast.Or: any,
}

# Whitelisted builtin functions
_SAFE_FUNCTIONS: dict[str, t.Callable] = {
    "len": len,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "abs": abs,
    "min": min,
    "max": max,
    "round": round,
    "isinstance": isinstance,
    "type": type,
}


class SafeEvalError(Exception):
    """Raised when an expression contains unsafe operations."""


def _eval_node(node: ast.AST, context: dict[str, t.Any]) -> t.Any:
    """Recursively evaluate an AST node against a context dict."""

    # Constants (strings, numbers, booleans, None)
    if isinstance(node, ast.Constant):
        return node.value

    # Variable name lookup
    if isinstance(node, ast.Name):
        if node.id in context:
            return context[node.id]
        if node.id in _SAFE_FUNCTIONS:
            return _SAFE_FUNCTIONS[node.id]
        # Return None for undefined vars instead of crashing
        return None

    # Binary operations: a + b, a > b, etc.
    if isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in _BIN_OPS:
            raise SafeEvalError(f"Unsupported binary operator: {op_type.__name__}")
        left = _eval_node(node.left, context)
        right = _eval_node(node.right, context)
        return _BIN_OPS[op_type](left, right)

    # Unary operations: not x, -x, +x
    if isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in _UNARY_OPS:
            raise SafeEvalError(f"Unsupported unary operator: {op_type.__name__}")
        operand = _eval_node(node.operand, context)
        return _UNARY_OPS[op_type](operand)

    # Boolean operations: a and b, a or b
    if isinstance(node, ast.BoolOp):
        op_type = type(node.op)
        if op_type not in _BOOL_OPS:
            raise SafeEvalError(f"Unsupported boolean operator: {op_type.__name__}")
        values = [_eval_node(v, context) for v in node.values]
        return _BOOL_OPS[op_type](values)

    # Comparisons: a == b, a > b, a in b, etc.
    if isinstance(node, ast.Compare):
        left = _eval_node(node.left, context)
        for op, comparator in zip(node.ops, node.comparators):
            op_type = type(op)
            if op_type not in _CMP_OPS:
                raise SafeEvalError(f"Unsupported comparison: {op_type.__name__}")
            right = _eval_node(comparator, context)
            if not _CMP_OPS[op_type](left, right):
                return False
            left = right
        return True

    # Function calls — only whitelisted functions
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise SafeEvalError("Only direct function calls are allowed")
        func_name = node.func.id
        if func_name not in _SAFE_FUNCTIONS:
            raise SafeEvalError(f"Function not allowed: {func_name}")
        args = [_eval_node(arg, context) for arg in node.args]
        kwargs = {kw.arg: _eval_node(kw.value, context) for kw in node.keywords}
        return _SAFE_FUNCTIONS[func_name](*args, **kwargs)

    # Attribute access — safe for dict key access patterns like obj.attr
    if isinstance(node, ast.Attribute):
        value = _eval_node(node.value, context)
        if isinstance(value, dict):
            if node.attr.startswith("_"):
                raise SafeEvalError(f"Access to private attribute '{node.attr}' not allowed")
            return value.get(node.attr)
        raise SafeEvalError(f"Attribute access on non-dict: {node.attr}")

    # Subscript access — dict[key], list[index]
    if isinstance(node, ast.Subscript):
        value = _eval_node(node.value, context)
        if isinstance(node.slice, ast.Index):  # Python < 3.9
            key = _eval_node(node.slice.value, context)
        else:
            key = _eval_node(node.slice, context)
        if isinstance(value, (dict, list)):
            return value[key]
        raise SafeEvalError("Subscript access only allowed on dict/list")

    # List literals: [1, 2, 3]
    if isinstance(node, ast.List):
        return [_eval_node(elt, context) for elt in node.elts]

    # Tuple literals: (1, 2, 3)
    if isinstance(node, ast.Tuple):
        return tuple(_eval_node(elt, context) for elt in node.elts)

    # Dict literals: {"key": value}
    if isinstance(node, ast.Dict):
        keys = [_eval_node(k, context) if k else None for k in node.keys]
        values = [_eval_node(v, context) for v in node.values]
        return dict(zip(keys, values))

    # IfExp: x if condition else y
    if isinstance(node, ast.IfExp):
        test = _eval_node(node.test, context)
        if test:
            return _eval_node(node.body, context)
        return _eval_node(node.orelse, context)

    # Starred: *args unpacking
    if isinstance(node, ast.Starred):
        return _eval_node(node.value, context)

    raise SafeEvalError(f"Unsupported expression: {type(node).__name__}")


def safe_eval(expression: str, context: dict[str, t.Any] | None = None) -> t.Any:
    """
    Safely evaluate a Python expression against a context dict.

    Args:
        expression: A Python expression string (e.g., 'status == "active"')
        context: Dict of variable names to values

    Returns:
        The evaluated result, or None on error (never raises on bad expressions)

    Raises:
        SafeEvalError: If the expression contains genuinely unsafe operations
    """
    if not expression or not expression.strip():
        return None

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return None

    try:
        return _eval_node(tree.body, context or {})
    except (SafeEvalError, KeyError, IndexError, TypeError, ZeroDivisionError):
        raise
    except Exception:
        return None
