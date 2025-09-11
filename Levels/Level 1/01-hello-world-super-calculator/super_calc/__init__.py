"""
super_calc package

Modules:
- models: Data structures used across the app.
- calculator: Core calculator state and operations.
- expr: Safe arithmetic expression evaluator.
- persistence: Saving/loading state to JSON.
- cli: Interactive command-line interface.

This package provides a modular, testable implementation of the Super Calculator.
"""

from .models import Calculation
from .calculator import Calculator
from .persistence import StateStore
from .cli import SuperCalcCLI

__all__ = [
    "Calculation",
    "Calculator",
    "StateStore",
    "SuperCalcCLI",
]

