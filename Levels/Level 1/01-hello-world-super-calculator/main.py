"""
main.py — App entrypoint for Super Calculator

Responsibilities
- Parse CLI flags and construct application components.
- Start the interactive CLI loop.

Flags
- --precision N: Format results to N decimal places, trimming trailing zeros.
- --state PATH: Persist memory/history JSON at PATH between runs.

Pseudocode
  parse_args()
  calc = Calculator()
  store = StateStore()
  cli = SuperCalcCLI(calc, store, precision=args.precision, state_path=args.state)
  cli.run()
"""

from typing import Optional

from super_calc.calculator import Calculator
from super_calc.persistence import StateStore
from super_calc.cli import SuperCalcCLI


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(description="Super Calculator")
    parser.add_argument(
        "--precision",
        type=int,
        default=None,
        help="Decimal places for output formatting (e.g., --precision 4)",
    )
    parser.add_argument(
        "--state",
        type=str,
        default=None,
        help="Path to JSON file to persist memory and history between runs",
    )
    parser.add_argument(
        "--decimal",
        action="store_true",
        help="Use Decimal arithmetic mode (optional; wiring in later steps)",
    )
    return parser.parse_args()


def main(precision: Optional[int] = None, state_path: Optional[str] = None, decimal: bool = False) -> None:
    calc = Calculator()
    store = StateStore()
    SuperCalcCLI(calc, store, precision=precision, state_path=state_path, decimal_mode=decimal).run()


if __name__ == "__main__":
    args = parse_args()
    main(precision=args.precision, state_path=args.state, decimal=args.decimal)
