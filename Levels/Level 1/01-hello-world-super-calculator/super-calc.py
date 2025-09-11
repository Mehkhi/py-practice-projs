"""
Compatibility wrapper for the previous single-file script.

This file now delegates to main.py to run the application. Keeping this
wrapper allows existing commands like:
  python3 super-calc.py --precision 2 --state state.json
to keep working after the refactor to a multi-module package.

Pseudocode
  from main import main, parse_args
  if __name__ == '__main__':
      args = parse_args()
      main(precision=args.precision, state_path=args.state)
"""

from main import main, parse_args  # type: ignore


if __name__ == "__main__":
    args = parse_args()
    main(precision=args.precision, state_path=args.state)
