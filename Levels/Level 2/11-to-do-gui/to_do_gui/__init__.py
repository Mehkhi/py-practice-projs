"""
To-Do GUI Application Package.

A comprehensive to-do list management application with a graphical user interface
built using Tkinter. Features include task creation, editing, deletion, completion
tracking, priority management, due dates, and search functionality.

Main Components:
- core: Task and TaskManager classes for business logic
- gui: Tkinter-based graphical user interface
- main: Application entry point

Usage:
    python -m to_do_gui
    or
    from to_do_gui import TodoGUI
    app = TodoGUI()
    app.run()
"""

__version__ = "1.0.0"
__author__ = "To-Do GUI Team"

from .core import Task, TaskManager
from .gui import TodoGUI
from .main import main

__all__ = ['Task', 'TaskManager', 'TodoGUI', 'main']
