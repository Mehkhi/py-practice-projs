"""
expr.py — Safe arithmetic expression evaluator

Responsibilities
- Parse and evaluate arithmetic expressions with +, -, *, /, parentheses,
  and unary +/- while respecting operator precedence.
- Guard against unsafe constructs by using Python's `ast` module and
  allowing only a safe subset of nodes.
- Support read-only variables in expressions: `ans` (last result), `mem` (memory).

API
- evaluate(expr: str, symbols: dict[str, float] | None = None, decimal: bool = False) -> float
  Returns a numeric result.
  Raises ZeroDivisionError on division by zero, ValueError on malformed/unsupported input.

Pseudocode
  function evaluate(expr, symbols):
      parse AST in eval mode
      recursively eval nodes:
          Name: lookup in symbols (case-insensitive), else error
          BinOp: eval left/right; apply Add/Sub/Mult/Div (raise ZeroDivisionError on /0)
          UnaryOp: apply UAdd/USub
          Constant/Num: return float value
          else: error
      return float(result)
"""

from typing import Optional, Union, Dict
import ast
import math
from decimal import Decimal

# 2.1 — Whitelists for functions and constants (used in later steps)
FUNCS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
    "round": round,
}

CONSTS = {
    "pi": math.pi,
    "e": math.e,
}


def evaluate(expr: str, symbols: Optional[Dict[str, float]] = None, decimal: bool = False) -> float:
    # Build symbol table; convert to Decimal if requested
    if decimal:
        syms = {k.lower(): Decimal(str(v)) for k, v in (symbols or {}).items()}
        ZERO = Decimal("0")
    else:
        syms = {k.lower(): float(v) for k, v in (symbols or {}).items()}
        ZERO = 0.0

    def eval_node(node) -> Union[float, None]:
        if isinstance(node, ast.Expression):
            return eval_node(node.body)
        if isinstance(node, ast.Call):
            if decimal:
                # First cut: functions are unavailable in decimal mode
                raise ValueError("functions unavailable in decimal mode")
            # Only allow function calls by simple name with positional args
            if not isinstance(node.func, ast.Name):
                raise ValueError("Unsupported call target")
            fname = getattr(node.func, 'id', None)
            if not isinstance(fname, str):
                raise ValueError("Unsupported function name")
            key = fname.lower()
            if key not in FUNCS:
                raise ValueError(f"Unsupported function: {fname}")
            # No keyword arguments (including **kwargs)
            if getattr(node, 'keywords', None):
                raise ValueError("Keyword arguments are not allowed")
            # No starred positional arguments (*args)
            for a in getattr(node, 'args', []) or []:
                if isinstance(a, getattr(ast, 'Starred', tuple())):
                    raise ValueError("Starred arguments are not allowed")
            args = [eval_node(arg) for arg in node.args]
            if any(a is None for a in args):
                return None
            # 11.3 — targeted function arity messages
            arity: Dict[str, tuple] = {
                "sqrt": (1,),
                "sin": (1,),
                "cos": (1,),
                "tan": (1,),
                "log": (1, 2),
                "log10": (1,),
                "exp": (1,),
                "abs": (1,),
                "round": (1, 2),
            }
            allowed_counts = arity.get(key)
            if allowed_counts is not None and len(args) not in allowed_counts:
                # Build human-friendly arity text
                if allowed_counts == (1, 2):
                    expected = "1 or 2"
                else:
                    expected = ", ".join(str(x) for x in allowed_counts)
                raise ValueError(f"{fname} expects {expected} arguments.")
            if key == 'round' and len(args) == 2:
                # Python round expects the second argument (ndigits) as int
                try:
                    args[1] = int(args[1])
                except Exception:
                    raise ValueError("round() ndigits must be an integer")
            result = FUNCS[key](*args)
            return float(result)
        if isinstance(node, ast.Name):
            name = getattr(node, 'id', None)
            if not isinstance(name, str):
                raise ValueError("Unsupported identifier")
            key = name.lower()
            if key in syms:
                return syms[key]
            if key in CONSTS:
                return Decimal(str(CONSTS[key])) if decimal else float(CONSTS[key])
            raise ValueError(f"Unknown identifier: {name}")
        if isinstance(node, ast.BinOp):
            left = eval_node(node.left)
            right = eval_node(node.right)
            if left is None or right is None:
                return None
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                if right == ZERO:
                    raise ZeroDivisionError("division by zero")
                return left / right
            if hasattr(ast, 'Mod') and isinstance(node.op, getattr(ast, 'Mod')):
                if right == ZERO:
                    raise ZeroDivisionError("division by zero")
                return left % right
            if hasattr(ast, 'Pow') and isinstance(node.op, getattr(ast, 'Pow')):
                return left ** right
            if hasattr(ast, 'FloorDiv') and isinstance(node.op, getattr(ast, 'FloorDiv')):
                if right == ZERO:
                    raise ZeroDivisionError("division by zero")
                return left // right
            raise ValueError("Unsupported operator")
        if isinstance(node, ast.UnaryOp):
            operand = eval_node(node.operand)
            if operand is None:
                return None
            if isinstance(node.op, ast.UAdd):
                return +operand
            if isinstance(node.op, ast.USub):
                return -operand
            raise ValueError("Unsupported unary operator")
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return Decimal(str(node.value)) if decimal else float(node.value)
            raise ValueError("Only numeric constants allowed")
        if hasattr(ast, 'Num') and isinstance(node, getattr(ast, 'Num')):
            return Decimal(str(node.n)) if decimal else float(node.n)
        raise ValueError("Unsupported expression element")

    tree = ast.parse(expr, mode='eval')
    # 10.1 — Hardening: ensure only allowed AST node types are present
    allowed = {
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Name,
        ast.Load,
        ast.Call,
        ast.Constant,
    }
    # Back-compat for older Python versions where numbers are ast.Num
    if hasattr(ast, 'Num'):
        allowed.add(getattr(ast, 'Num'))
    # Operator node classes that appear in the tree
    op_nodes = [
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv,
        ast.UAdd, ast.USub,
    ]
    allowed.update(op_nodes)
    for node in ast.walk(tree):
        if not isinstance(node, tuple(allowed)):
            raise ValueError("Unsupported expression element")
    value = eval_node(tree)
    # For consistency with existing callers and persistence, return float
    return float(value)
