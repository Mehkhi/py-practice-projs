"""
cli.py — Command-line interface for the Super Calculator

Responsibilities
- Manage user interaction via a single input prompt (REPL-style).
- Interpret input lines as either commands (m+, m-, mr, undo, redo, hist, quit)
  or arithmetic expressions to evaluate.
- Use `expr.evaluate` to compute results, and `Calculator` to manage state.
- Use `StateStore` to load/save state across runs.

Design
- Formatting is kept here to keep non-I/O modules pure.
- Only a small command alias table is used; math expressions are not tokenized here.
- Expressions may reference variables: `ans` (last result) and `mem` (memory).

Pseudocode
  class SuperCalcCLI:
      init(calc, store, precision, state_path)
      normalize_command(raw): map aliases to canonical command or None
      format_number(value): apply precision & trim trailing zeros
      print_history(): pretty-print history entries
      read_line(prompt): input wrapper that returns None on EOF
      run():
          if state_path -> load and print summary
          print instructions
          loop:
              line = read_line('calc> ')
              if alias->quit: save if needed; break
              if alias in memory/undo/redo/hist: handle and continue
              else: treat as expression
                    value = evaluate(line, symbols={ans: last_result or 0.0, mem: memory})
                    print explicit division-by-zero vs malformed errors
                    record result and display
"""

from typing import Optional
import re
import os
import atexit
import math

from .calculator import Calculator
from .persistence import StateStore
from .expr import evaluate, FUNCS, CONSTS
from .models import Calculation


ALIASES = {
    # Memory
    "m+": "m+",
    "m-": "m-",
    "mr": "mr",
    "recall": "mr",
    # History / Undo / Redo
    "u": "undo",
    "undo": "undo",
    "r": "redo",
    "redo": "redo",
    "h": "hist",
    "hist": "hist",
    "history": "hist",
    # Quit
    "q": "quit",
    "quit": "quit",
    "x": "quit",
    "exit": "quit",
    # Help
    "help": "help",
    "?": "help",
}


 


class SuperCalcCLI:
    """Interactive CLI for Super Calc.

    Handles REPL input, command parsing (help, hist, precision, clear, format, config),
    and delegates evaluation/formatting while keeping non-I/O modules pure.
    """
    def __init__(self, calc: Calculator, store: StateStore, precision: Optional[int] = None, state_path: Optional[str] = None, decimal_mode: bool = False):
        self.calc = calc
        self.store = store
        self.precision = precision
        self.state_path = state_path
        self.decimal_mode = decimal_mode
        # Keep calculator's persisted flag in sync
        try:
            self.calc.decimal_mode = bool(decimal_mode)
            self.calc.precision = precision
        except Exception:
            pass
        # 8.1 Formatting options (defaults)
        self.format_thousands: bool = False
        self.format_notation: str = "plain"  # one of: plain, scientific, engineering
        # 6.1 Readline history (optional)
        self._readline = None
        self._histfile = None
        try:
            import readline  # type: ignore

            self._readline = readline
            self._histfile = os.path.join(os.path.expanduser("~"), ".super_calc_history")
            try:
                self._readline.read_history_file(self._histfile)
            except FileNotFoundError:
                pass
            except Exception:
                # Ignore history issues silently
                pass

            def _save_history():
                try:
                    if self._readline and self._histfile:
                        self._readline.write_history_file(self._histfile)
                except Exception:
                    pass

            atexit.register(_save_history)
        except Exception:
            # Readline not available (e.g., some platforms). Ignore.
            pass

    @staticmethod
    def normalize_command(raw: Optional[str]) -> Optional[str]:
        if raw is None:
            return None
        token = raw.strip().lower()
        if not token:
            return None
        return ALIASES.get(token)

    def read_line(self, prompt: str) -> Optional[str]:
        """Read a single line from stdin; return None on EOF (to trigger quit)."""
        try:
            return input(prompt)
        except EOFError:
            return None

    def print_history(self):
        """Pretty-print the full calculation history using current formatter."""
        if not self.calc.history:
            print("History is empty.")
            return
        for idx, entry in enumerate(self.calc.history, start=1):
            if entry.expr:
                print(f"{idx}) {entry.expr} = {self._fmt(entry.result)}")
            else:
                print(
                    f"{idx}) {entry.op} {self._fmt(entry.a)} "
                    f"{self._fmt(entry.b)} = {self._fmt(entry.result)}"
                )

    def _fmt(self, value):
        """Format numbers with precision, thousands separators, and notation modes."""
        # Extended formatter with thousands separators and notation modes
        if value is None:
            return "undefined"
        val = float(value)
        prec = self.precision
        notation = (self.format_notation or "plain").lower()
        if notation == "scientific":
            p = 6 if prec is None else prec
            s = f"{val:.{p}e}"
            return s
        if notation == "engineering":
            if val == 0:
                return "0"
            exp = int(math.floor(math.log10(abs(val)) / 3) * 3)
            scaled = val / (10 ** exp)
            p = 6 if prec is None else prec
            body = f"{scaled:.{p}f}"
            body = body.rstrip("0").rstrip(".")
            if body == "-0":
                body = "0"
            return f"{body}e{exp:+d}"
        # plain
        if prec is None:
            if self.format_thousands:
                try:
                    return format(val, ",")
                except Exception:
                    return str(val)
            return str(val)
        # fixed with trimming
        s = f"{val:.{prec}f}"
        s = s.rstrip("0").rstrip(".")
        if s == "-0":
            s = "0"
        if self.format_thousands:
            sign = "-" if s.startswith("-") else ""
            rest = s[1:] if sign else s
            if "." in rest:
                integer, frac = rest.split(".", 1)
            else:
                integer, frac = rest, None
            try:
                integer_commas = f"{int(integer):,}"
            except Exception:
                integer_commas = integer
            s = sign + integer_commas + ("." + frac if frac else "")
        return s

    def print_help(self):
        """Print contextual help for supported operators, commands, and examples."""
        # 4.2 — Implement help text content
        print("\n=== SuperCalc Help ===")
        # 4.2.1 Operators
        print("Operators:")
        print("  +  -  *  /  **  %  //  ( )  unary + -")
        # 4.2.2 Variables
        user_vars = ", ".join(sorted(self.calc.vars.keys())) if self.calc.vars else "(none)"
        print("Variables:")
        print("  ans (last result), mem (memory), user vars:", user_vars)
        # 4.2.3 Functions and constants
        if self.decimal_mode:
            print("Functions: (disabled in decimal mode)")
        else:
            print("Functions:")
            print("  ", ", ".join(sorted(FUNCS.keys())))
        print("Constants:")
        print("  ", ", ".join(sorted(CONSTS.keys())))
        # 4.2.4 Commands
        print("Commands:")
        print("  m+   m-   mr   undo   redo   hist [N|/pattern/]")
        print("  precision N | precision off   clear [all|hist|mem|vars]   help   quit")
        print("  format thousands on|off   format notation plain|scientific|engineering")
        print("  config   (show current settings)")
        print("Examples:")
        print("  hist 5")
        print("  hist /add/")
        print("  precision off")
        print("  format notation scientific")
        print("  x = 2+3")
        print("  ans*2")
        # 4.2.5 Assignment syntax
        print("Assignment:")
        print("  name = expression   e.g.,   x = 2+3   then   x*2")
        # Decimal mode status
        print("Mode:")
        print("  Decimal mode:", "ON (functions disabled)" if self.decimal_mode else "OFF")

    def _print_syntax_error(self, src: str, err: SyntaxError):
        """Show a syntax error with the offending line and a caret under the offset."""
        print("Syntax error")
        line = (getattr(err, 'text', None) or src or '').rstrip('\n')
        print(f"  {line}")
        try:
            off = int(getattr(err, 'offset', 0) or 0)
        except Exception:
            off = 0
        if off > 0:
            caret = " " * (off - 1)
            print(f"  {caret}^")

    def _print_malformed(self, err: Exception):
        """Emit targeted guidance for common evaluation errors; fallback to generic help."""
        msg = str(err) if err else ''
        # Specific guidance for common cases
        if isinstance(err, ValueError) and msg.endswith(" arguments.") and "expects" in msg:
            # Pass through targeted arity message (e.g., "round expects 1 or 2 arguments.")
            print(msg)
            return
        if isinstance(err, ValueError) and msg.startswith("Unknown identifier: "):
            ident = msg.split(":", 1)[1].strip()
            print(f"Unknown identifier {ident}. Define it first (e.g., x = 2+3) or use ans/mem.")
            return
        if isinstance(err, ValueError) and msg.startswith("Unsupported function: "):
            allowed = ", ".join(sorted(FUNCS.keys()))
            func = msg.split(":", 1)[1].strip()
            print(f"Unsupported function {func}. Allowed: {allowed}.")
            return
        if "Unsupported operator" in msg:
            print("Unsupported operator. Supported: + - * / ** % // (with parentheses).")
            return
        if "Unsupported expression element" in msg:
            print("Unsupported construct. Use numbers/variables, functions, + - * / ** % //, and parentheses.")
            return
        # Generic guidance
        print("Malformed expression. Use numbers/variables (ans, mem, user vars), functions, + - * / ** % //, and parentheses.")

    def run(self) -> None:
        """Main REPL loop: load state, show banner, parse commands/expressions until quit."""
        if self.state_path:
            loaded = self.store.load(self.state_path)
            if loaded is not None:
                # Accept multiple tuple shapes for backward compatibility
                # (memory, history, [vars], [decimal], [fmt_thousands], [fmt_notation], [precision])
                memory = None
                hist_list = []
                vars_map = {}
                decimal_mode = self.decimal_mode
                fmt_thousands = self.format_thousands
                fmt_notation = self.format_notation
                precision = self.precision
                if isinstance(loaded, tuple):
                    L = len(loaded)
                    if L >= 1:
                        memory = loaded[0]
                    if L >= 2:
                        hist_list = loaded[1]
                    if L >= 3:
                        vars_map = loaded[2]
                    if L >= 4:
                        decimal_mode = loaded[3]
                    if L >= 5:
                        fmt_thousands = loaded[4]
                    if L >= 6:
                        fmt_notation = loaded[5]
                    if L >= 7:
                        precision = loaded[6]
                self.calc.memory = memory
                self.calc.history = hist_list
                self.calc.vars = vars_map
                # Sync decimal mode from persisted state
                self.calc.decimal_mode = bool(decimal_mode)
                self.decimal_mode = bool(decimal_mode)
                # Sync formatting preferences
                self.format_thousands = bool(fmt_thousands)
                self.format_notation = str(fmt_notation)
                self.calc.format_thousands = self.format_thousands
                self.calc.format_notation = self.format_notation
                # Sync precision
                self.precision = precision
                self.calc.precision = precision
                self.calc.last_result = self.calc.history[-1].result if self.calc.history else None
                print(
                    f"Loaded state: memory={self._fmt(self.calc.memory)}, "
                    f"history entries={len(self.calc.history)}."
                )

        print("Type an expression (e.g., 2+3*4) or command (m+, m-, mr, undo, redo, hist, quit)")
        print("You can also use variables: ans (last result), mem (memory)")
        if self.decimal_mode:
            print("Functions: disabled in decimal mode")
            print("Constants: pi, e")
        else:
            print("Functions: sqrt, sin, cos, tan, log, log10, exp, abs, round")
            print("Constants: pi, e")
        while True:
            line = self.read_line("calc> ")
            if line is None:
                line = "quit"
            line = line.strip()
            if not line:
                continue

            # History: hist N (show last N entries)
            m = re.match(r"^\s*(?:hist|history|h)\s+(\d+)\s*$", line, re.I)
            if m:
                try:
                    n = int(m.group(1))
                except Exception:
                    n = 0
                if n <= 0:
                    print("Usage: hist N (N>0).")
                    continue
                if not self.calc.history:
                    print("History is empty.")
                    continue
                entries = self.calc.history[-n:]
                start_idx = len(self.calc.history) - len(entries) + 1
                for i, entry in enumerate(entries, start=start_idx):
                    if entry.expr:
                        print(f"{i}) {entry.expr} = {self._fmt(entry.result)}")
                    else:
                        print(
                            f"{i}) {entry.op} {self._fmt(entry.a)} "
                            f"{self._fmt(entry.b)} = {self._fmt(entry.result)}"
                        )
                continue

            # History: hist /pattern/ (regex or substring, case-insensitive)
            m = re.match(r"^\s*(?:hist|history|h)\s+/(.*?)/\s*$", line, re.I)
            if m:
                pattern = m.group(1)
                rx = None
                try:
                    rx = re.compile(pattern, re.I)
                except re.error:
                    rx = None
                matched = []
                for idx, entry in enumerate(self.calc.history, start=1):
                    target = (entry.expr if entry.expr else (entry.op or "")) or ""
                    if rx is not None:
                        ok = bool(rx.search(target))
                    else:
                        ok = pattern.lower() in target.lower()
                    if ok:
                        matched.append((idx, entry))
                if not matched:
                    print("No matching history entries.")
                    continue
                for i, entry in matched:
                    if entry.expr:
                        print(f"{i}) {entry.expr} = {self._fmt(entry.result)}")
                    else:
                        print(
                            f"{i}) {entry.op} {self._fmt(entry.a)} "
                            f"{self._fmt(entry.b)} = {self._fmt(entry.result)}"
                        )
                continue

            # Assignment: name = expression
            if "=" in line and re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", line):
                name, rhs = line.split("=", 1)
                name = name.strip()
                rhs = rhs.strip()
                # Reserved identifiers cannot be assigned
                if name.lower() in ("ans", "mem"):
                    print("Cannot assign to reserved name 'ans' or 'mem'.")
                    continue
                try:
                    value = evaluate(rhs, symbols=self.calc.get_symbols(), decimal=self.decimal_mode)
                except ZeroDivisionError:
                    print("Result: undefined (division by zero).")
                    continue
                except SyntaxError as e:
                    self._print_syntax_error(rhs, e)
                    continue
                except Exception as e:
                    if self.decimal_mode and isinstance(e, ValueError) and "functions unavailable in decimal mode" in str(e):
                        print("Functions are disabled in decimal mode.")
                    else:
                        self._print_malformed(e)
                    continue
                self.calc.set_var(name, value)
                print(f"Assigned: {name} = {self._fmt(value)}.")
                continue

            # Config: precision off|none
            m = re.match(r"^\s*precision\s+(off|none)\s*$", line, re.I)
            if m:
                self.precision = None
                self.calc.precision = None
                print("Precision turned off.")
                continue

            # Config: precision N
            m = re.match(r"^\s*precision\s+(\d+)\s*$", line, re.I)
            if m:
                original = int(m.group(1))
                clamped = max(0, min(12, original))
                self.precision = clamped
                self.calc.precision = clamped
                if clamped != original:
                    print(f"Precision set to {clamped} (clamped from {original}).")
                else:
                    print(f"Precision set to {self.precision}.")
                continue

            # Config: invalid precision usage
            if re.match(r"^\s*precision\b", line, re.I):
                print("Usage: precision N (0-12) or precision off.")
                continue

            # Config: clear [hist|mem|vars|all]
            m = re.match(r"^\s*clear\s+(\w+)\s*$", line, re.I)
            if m:
                target = m.group(1).lower()
                if target == "hist":
                    self.calc.history.clear()
                    self.calc.redo_stack.clear()
                    print("History cleared")
                elif target == "mem":
                    self.calc.memory = 0.0
                    print("Memory cleared")
                elif target == "vars":
                    self.calc.vars.clear()
                    print("Variables cleared")
                elif target == "all":
                    self.calc.history.clear()
                    self.calc.redo_stack.clear()
                    self.calc.memory = 0.0
                    self.calc.vars.clear()
                    self.calc.last_result = None
                    print("All cleared (history, memory, variables, last result)")
                else:
                    print("Unknown clear target. Use: clear hist|mem|vars|all")
                continue

            # Formatting: format thousands on|off
            m = re.match(r"^\s*format\s+thousands\s+(on|off)\s*$", line, re.I)
            if m:
                self.format_thousands = (m.group(1).lower() == "on")
                self.calc.format_thousands = self.format_thousands
                print(f"Thousands separators: {'ON' if self.format_thousands else 'OFF' }.")
                continue

            # Formatting: format notation plain|scientific|engineering
            m = re.match(r"^\s*format\s+notation\s+(plain|scientific|engineering)\s*$", line, re.I)
            if m:
                self.format_notation = m.group(1).lower()
                self.calc.format_notation = self.format_notation
                print(f"Notation set to {self.format_notation}.")
                continue

            # Formatting: invalid usage catch-all
            if re.match(r"^\s*format\b", line, re.I):
                print("Usage: format thousands on|off; format notation plain|scientific|engineering.")
                continue

            # Show current configuration
            if re.match(r"^\s*config(\s+show)?\s*$", line, re.I):
                prec_str = "off" if self.precision is None else str(self.precision)
                print("Config:")
                print(f"  Precision: {prec_str}")
                print(f"  Decimal mode: {'ON' if self.decimal_mode else 'OFF'}")
                print(f"  Thousands: {'ON' if self.format_thousands else 'OFF'}")
                print(f"  Notation: {self.format_notation}")
                continue

            cmd = self.normalize_command(line)
            if cmd == "help":
                self.print_help()
                continue
            if cmd in ("quit",):
                if self.state_path:
                    try:
                        self.store.save(self.state_path, self.calc)
                        print(f"Saved state to {self.state_path}")
                    except Exception as e:
                        print(f"Warning: failed to save state: {e}")
                print("Goodbye!")
                break

            if cmd in ("m+", "m-", "mr", "undo", "redo", "hist"):
                if cmd == "m+":
                    if not self.calc.mem_add_last():
                        print("No last result to add. Perform a calculation first.")
                    else:
                        print(f"Memory updated: memory = {self._fmt(self.calc.memory)}")
                elif cmd == "m-":
                    if not self.calc.mem_sub_last():
                        print("No last result to subtract. Perform a calculation first.")
                    else:
                        print(f"Memory updated: memory = {self._fmt(self.calc.memory)}")
                elif cmd == "mr":
                    print(f"Memory recall: {self._fmt(self.calc.mem_recall())}")
                elif cmd == "undo":
                    entry = self.calc.undo()
                    if entry is None:
                        print("Nothing to undo.")
                    else:
                        if entry.expr:
                            print(f"Undone: {entry.expr} = {self._fmt(entry.result)}.")
                        else:
                            print(
                                f"Undone: {entry.op} {self._fmt(entry.a)} "
                                f"{self._fmt(entry.b)} = {self._fmt(entry.result)}."
                            )
                elif cmd == "redo":
                    entry = self.calc.redo()
                    if entry is None:
                        print("Nothing to redo.")
                    else:
                        if entry.expr:
                            print(f"Redone: {entry.expr} = {self._fmt(entry.result)}.")
                        else:
                            print(
                                f"Redone: {entry.op} {self._fmt(entry.a)} "
                                f"{self._fmt(entry.b)} = {self._fmt(entry.result)}."
                            )
                else:  # hist
                    self.print_history()
                continue

            # Otherwise, treat as expression
            try:
                result = evaluate(line, symbols=self.calc.get_symbols(), decimal=self.decimal_mode)
            except ZeroDivisionError:
                print("Result: undefined (division by zero).")
                continue
            except SyntaxError as e:
                self._print_syntax_error(line, e)
                continue
            except Exception as e:
                if self.decimal_mode and isinstance(e, ValueError) and "functions unavailable in decimal mode" in str(e):
                    print("Functions are disabled in decimal mode.")
                else:
                    self._print_malformed(e)
                continue

            # Special case: plain 'mem' or 'ans' should not change last_result/history
            if line.strip().lower() in ("mem", "ans"):
                print(f"Result: {line} = {self._fmt(result)}.")
                continue

            self.calc.record_expr(line, result)
            print(f"Result: {line} = {self._fmt(result)}.")
