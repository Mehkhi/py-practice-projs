#!/bin/bash
# Run all project tests using the venv with pygame installed.
# Usage: ./run_tests.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$SCRIPT_DIR/.venv/bin/python3"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at $SCRIPT_DIR/.venv"
    echo "Create it with: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

exec "$VENV_PYTHON" -m unittest discover -t "$SCRIPT_DIR" -s "$SCRIPT_DIR/tests" -p "test_*.py"
