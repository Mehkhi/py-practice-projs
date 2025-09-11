"""
calculator.py — Core calculator state and logic

Responsibilities
- Maintain calculator state: memory, last_result, history, redo_stack.
- Provide basic binary operations (add, sub, mul, div) for completeness.
- Record results into history (both binary ops and expression results).
- Support memory commands (m+, m-, mr) and undo/redo of calculations.

Design
- This module does not perform I/O and does not parse expressions.
  The CLI calls into this module after parsing/evaluating input.

Pseudocode
  class Calculator:
      init: memory=0, last_result=None, history=[], redo_stack=[]
      add/sub/mul/div(a,b): compute (div returns None for b==0)
      perform(op,a,b): clear redo; compute; if result ok -> update last_result, append Calculation
      record_expr(expr, result): clear redo; set last_result; append Calculation
      mem_add_last/mem_sub_last: add/sub last_result to/from memory; return success bool
      mem_recall(): return memory
      undo(): pop from history -> redo_stack; update last_result; return entry or None
      redo(): pop from redo_stack -> history; update last_result; return entry or None
"""

from typing import Optional, List

from .models import Calculation


class Calculator:
    def __init__(self):
        self.memory: float = 0.0
        self.history: List[Calculation] = []
        self.redo_stack: List[Calculation] = []
        self.last_result: Optional[float] = None
        # App/config state (persisted via StateStore)
        self.decimal_mode: bool = False
        self.format_thousands: bool = False
        self.format_notation: str = "plain"
        self.precision: Optional[int] = None
        # User-defined variables for expression evaluation
        self.vars: dict[str, float] = {}

    # Core binary operations
    def add(self, a: float, b: float) -> float:
        return a + b

    def sub(self, a: float, b: float) -> float:
        return a - b

    def mul(self, a: float, b: float) -> float:
        return a * b

    def div(self, a: float, b: float) -> Optional[float]:
        return None if b == 0 else a / b

    def perform(self, op: str, a: float, b: float) -> Optional[float]:
        self.redo_stack.clear()
        func = {
            "add": self.add,
            "sub": self.sub,
            "mul": self.mul,
            "div": self.div,
        }.get(op)
        if func is None:
            return None
        result = func(a, b)
        if result is None:
            self.last_result = None
            return None
        self.last_result = result
        self.history.append(Calculation(op=op, a=a, b=b, result=result))
        return result

    def record_expr(self, expr: str, result: Optional[float]) -> Optional[float]:
        self.redo_stack.clear()
        if result is None:
            self.last_result = None
            return None
        self.last_result = float(result)
        self.history.append(Calculation(expr=expr, result=self.last_result))
        return self.last_result

    # Variables helpers
    def set_var(self, name: str, value: float) -> None:
        self.vars[name.lower()] = float(value)

    def get_symbols(self) -> dict[str, float]:
        # Reserved identifiers override any user-defined variables
        return {
            **self.vars,
            "ans": 0.0 if self.last_result is None else float(self.last_result),
            "mem": float(self.memory),
        }

    # Memory features
    def mem_add_last(self) -> bool:
        if self.last_result is None:
            return False
        self.memory += self.last_result
        return True

    def mem_sub_last(self) -> bool:
        if self.last_result is None:
            return False
        self.memory -= self.last_result
        return True

    def mem_recall(self) -> float:
        return self.memory

    # Undo/Redo for calculations only
    def undo(self) -> Optional[Calculation]:
        if not self.history:
            return None
        entry = self.history.pop()
        self.redo_stack.append(entry)
        self.last_result = self.history[-1].result if self.history else None
        return entry

    def redo(self) -> Optional[Calculation]:
        if not self.redo_stack:
            return None
        entry = self.redo_stack.pop()
        self.history.append(entry)
        self.last_result = entry.result
        return entry
