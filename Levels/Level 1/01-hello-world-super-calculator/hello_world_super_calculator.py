#!/usr/bin/env python3
"""
Hello World Super Calculator
A command-line calculator with basic arithmetic operations, memory features, and expression parsing.
"""

import re
import json
import os
from typing import Union, List, Dict, Any


class SuperCalculator:
    """A super calculator with memory, history, and expression parsing capabilities."""

    def __init__(self):
        self.memory = 0.0
        self.history: List[Dict[str, Any]] = []
        self.history_index = -1
        self.history_file = "calculator_history.json"
        self.load_history()

    def load_history(self) -> None:
        """Load calculation history from file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    data = json.load(f)
                    self.history = data.get('history', [])
                    self.memory = data.get('memory', 0.0)
        except (json.JSONDecodeError, FileNotFoundError):
            self.history = []
            self.memory = 0.0

    def save_history(self) -> None:
        """Save calculation history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump({
                    'history': self.history,
                    'memory': self.memory
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")

    def add_to_history(self, expression: str, result: float) -> None:
        """Add a calculation to history."""
        self.history.append({
            'expression': expression,
            'result': result,
            'timestamp': self._get_timestamp()
        })
        self.history_index = len(self.history) - 1

    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def normalize_command(self, command: str) -> str:
        """Normalize and validate user commands."""
        command = command.strip().lower()

        # Command aliases
        aliases = {
            'add': '+',
            'plus': '+',
            'subtract': '-',
            'minus': '-',
            'multiply': '*',
            'times': '*',
            'divide': '/',
            'memory_add': 'm+',
            'memory_subtract': 'm-',
            'memory_recall': 'mr',
            'memory_clear': 'mc',
            'history': 'h',
            'undo': 'u',
            'redo': 'r',
            'quit': 'q',
            'exit': 'q',
            'help': '?'
        }

        return aliases.get(command, command)

    def validate_number(self, value: str) -> Union[float, None]:
        """Validate and convert string to number."""
        try:
            return float(value)
        except ValueError:
            return None

    def basic_operation(self, num1: float, operator: str, num2: float) -> Union[float, None]:
        """Perform basic arithmetic operations."""
        operations = {
            '+': lambda a, b: a + b,
            '-': lambda a, b: a - b,
            '*': lambda a, b: a * b,
            '/': lambda a, b: a / b if b != 0 else None
        }

        if operator in operations:
            result = operations[operator](num1, num2)
            if result is None and operator == '/':
                print("Error: Division by zero!")
                return None
            return result
        return None

    def parse_expression(self, expression: str) -> Union[float, None]:
        """Parse and evaluate mathematical expressions with precedence."""
        try:
            # Remove spaces and validate characters
            expression = expression.replace(' ', '')
            if not re.match(r'^[0-9+\-*/().]+$', expression):
                print("Error: Invalid characters in expression")
                return None

            # Replace 'mr' with memory value
            expression = expression.replace('mr', str(self.memory))

            # Evaluate expression safely
            result = eval(expression)
            return float(result)
        except ZeroDivisionError:
            print("Error: Division by zero!")
            return None
        except Exception as e:
            print(f"Error: Invalid expression - {e}")
            return None

    def memory_add(self, value: float) -> None:
        """Add value to memory."""
        self.memory += value
        print(f"Memory: {self.memory}")

    def memory_subtract(self, value: float) -> None:
        """Subtract value from memory."""
        self.memory -= value
        print(f"Memory: {self.memory}")

    def memory_recall(self) -> float:
        """Recall value from memory."""
        print(f"Memory: {self.memory}")
        return self.memory

    def memory_clear(self) -> None:
        """Clear memory."""
        self.memory = 0.0
        print("Memory cleared")

    def show_history(self) -> None:
        """Display calculation history."""
        if not self.history:
            print("No history available")
            return

        print("\n=== Calculation History ===")
        for i, entry in enumerate(self.history[-10:]):  # Show last 10 entries
            print(f"{i+1}. {entry['expression']} = {entry['result']} ({entry['timestamp']})")
        print("========================\n")

    def undo(self) -> Union[float, None]:
        """Undo last calculation."""
        if self.history_index > 0:
            self.history_index -= 1
            result = self.history[self.history_index]['result']
            print(f"Undo: {self.history[self.history_index]['expression']} = {result}")
            return result
        else:
            print("Nothing to undo")
            return None

    def redo(self) -> Union[float, None]:
        """Redo next calculation."""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            result = self.history[self.history_index]['result']
            print(f"Redo: {self.history[self.history_index]['expression']} = {result}")
            return result
        else:
            print("Nothing to redo")
            return None

    def show_help(self) -> None:
        """Display help information."""
        help_text = """
=== Super Calculator Help ===

Basic Operations:
  +, -, *, /          Basic arithmetic
  add, subtract, etc.  Command aliases

Memory Operations:
  M+                  Add to memory
  M-                  Subtract from memory
  MR                  Recall memory
  MC                  Clear memory

Advanced Features:
  Expression parsing  e.g., "2 + 3 * 4", "(10 + 5) / 3"
  MR in expressions   e.g., "MR + 5"

History:
  H                   Show history
  U                   Undo
  R                   Redo

Other:
  Q, EXIT             Quit
  ?                   Show this help

Examples:
  > 5 + 3
  > (10 + 5) * 2
  > MR + 10
  > M+ 5
============================
"""
        print(help_text)

    def process_command(self, command: str) -> bool:
        """Process user command. Returns False if should quit."""
        command = self.normalize_command(command)

        if command in ['q', 'quit', 'exit']:
            self.save_history()
            return False

        elif command == '?':
            self.show_help()

        elif command == 'h':
            self.show_history()

        elif command == 'u':
            self.undo()

        elif command == 'r':
            self.redo()

        elif command == 'mc':
            self.memory_clear()

        elif command == 'mr':
            self.memory_recall()

        elif command.startswith('m+'):
            # Memory add: M+ <number>
            parts = command.split()
            if len(parts) == 2:
                value = self.validate_number(parts[1])
                if value is not None:
                    self.memory_add(value)
                else:
                    print("Error: Invalid number")
            else:
                print("Usage: M+ <number>")

        elif command.startswith('m-'):
            # Memory subtract: M- <number>
            parts = command.split()
            if len(parts) == 2:
                value = self.validate_number(parts[1])
                if value is not None:
                    self.memory_subtract(value)
                else:
                    print("Error: Invalid number")
            else:
                print("Usage: M- <number>")

        else:
            # Try to evaluate as expression
            result = self.parse_expression(command)
            if result is not None:
                self.add_to_history(command, result)
                print(f"Result: {result}")

        return True

    def run(self) -> None:
        """Main calculator loop."""
        print("=== Hello World Super Calculator ===")
        print("Type '?' for help, 'q' to quit")
        print("=====================================")

        while True:
            try:
                command = input("\n> ").strip()
                if not command:
                    continue

                if not self.process_command(command):
                    break

            except KeyboardInterrupt:
                print("\nGoodbye!")
                self.save_history()
                break
            except EOFError:
                print("\nGoodbye!")
                self.save_history()
                break


def main():
    """Main entry point."""
    calculator = SuperCalculator()
    calculator.run()


if __name__ == "__main__":
    main()
