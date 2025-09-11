"""
models.py — Data structures for the Super Calculator

Responsibilities
- Define typed models that represent a calculation entry in history.

Key Types
- Calculation: a single history entry which may be expression-based (expr)
  or binary-op based (op, a, b). Exactly one of (expr) or (op,a,b) should be
  set for any given entry. `result` stores the numeric outcome.

Pseudocode
  define dataclass Calculation:
      fields: op?: str, a?: float, b?: float, expr?: str, result?: float
      method to_dict():
          base = {"result": result}
          if expr is set: base["expr"] = expr
          if op is set: base.update({"op": op, "a": a, "b": b})
          return base
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Calculation:
    op: Optional[str] = None
    a: Optional[float] = None
    b: Optional[float] = None
    expr: Optional[str] = None
    result: Optional[float] = None

    def to_dict(self):
        data = {"result": self.result}
        if self.expr is not None:
            data["expr"] = self.expr
        if self.op is not None:
            data.update({"op": self.op, "a": self.a, "b": self.b})
        return data

