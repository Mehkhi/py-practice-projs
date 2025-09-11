"""
persistence.py — Save/Load calculator state to JSON

Responsibilities
- Serialize calculator state (memory, variables, and history) to a JSON file.
- Deserialize JSON back into typed `Calculation` entries and variables.
- Be tolerant of older state formats that only had (op, a, b, result) tuples.

API
- class StateStore:
    save(path, calc): write JSON to path
    load(path) -> Optional[(memory: float, history: list[Calculation], vars: dict[str, float])]

Pseudocode
  class StateStore:
      save(path, calc):
          ensure directory exists
          data = { memory, vars, history=[entry.to_dict() for entry in calc.history] }
          json.dump to file
      load(path):
          if missing -> None
          try parse JSON
          build history entries:
              if entry has expr -> Calculation(expr, result)
              else -> Calculation(op, a, b, result)
          build vars_map = {k.lower(): float(v)} for k,v in data.get('vars', {}).items()
          return memory, history, vars_map
          except -> None
"""

from typing import Optional, List, Tuple, Dict

from .models import Calculation


class StateStore:
    def save(self, path: str, calc) -> None:
        import json, os
        data = {
            "memory": calc.memory,
            "vars": getattr(calc, "vars", {}),
            "decimal": bool(getattr(calc, "decimal_mode", False)),
            "format_thousands": bool(getattr(calc, "format_thousands", False)),
            "format_notation": str(getattr(calc, "format_notation", "plain")),
            "precision": getattr(calc, "precision", None),
            "history": [c.to_dict() for c in calc.history],
        }
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path: str) -> Optional[Tuple[float, List[Calculation], Dict[str, float], bool, bool, str, Optional[int]]]:
        import json, os
        if not path or not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            memory = float(data.get("memory", 0.0))
            hist_list: List[Calculation] = []
            for entry in data.get("history", []):
                expr = entry.get("expr")
                op = entry.get("op")
                a = entry.get("a")
                b = entry.get("b")
                res = entry.get("result")
                a_val = None if a is None else float(a)
                b_val = None if b is None else float(b)
                res_val = None if res is None else float(res)
                if expr is not None:
                    hist_list.append(Calculation(expr=expr, result=res_val))
                else:
                    hist_list.append(Calculation(op=op, a=a_val, b=b_val, result=res_val))
            vars_map: Dict[str, float] = {}
            for k, v in data.get("vars", {}).items():
                try:
                    vars_map[str(k).lower()] = float(v)
                except Exception:
                    # Skip unparseable values
                    continue
            decimal_mode = bool(data.get("decimal", False))
            fmt_thousands = bool(data.get("format_thousands", False))
            fmt_notation = str(data.get("format_notation", "plain"))
            prec_val = data.get("precision", None)
            try:
                precision = None if prec_val is None else int(prec_val)
            except Exception:
                precision = None
            return memory, hist_list, vars_map, decimal_mode, fmt_thousands, fmt_notation, precision
        except Exception:
            return None
