#!/usr/bin/env python3
"""
Demo script for the To-Do GUI application.

This script demonstrates how to use the To-Do GUI application
programmatically and shows some example tasks.
"""

import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from to_do_gui import TaskManager, Task


def demo_core_functionality():
    """Demonstrate core functionality without GUI."""
    print("=== To-Do GUI Core Functionality Demo ===\n")

    # Create a task manager
    manager = TaskManager("demo_tasks.json")

    # Add some sample tasks
    print("Adding sample tasks...")
    task1 = manager.add_task("Learn Python", "Complete Python basics course", "high")
    task2 = manager.add_task("Buy groceries", "Milk, bread, eggs", "medium", "2024-01-15")
    task3 = manager.add_task("Read book", "Finish 'Clean Code'", "low")
    task4 = manager.add_task("Exercise", "Go for a 30-minute run", "medium")

    print(f"Added {len(manager.get_all_tasks())} tasks\n")

    # Show all tasks
    print("All tasks:")
    for task in manager.get_all_tasks():
        status = "✓" if task.completed else "○"
        due_date = f" (Due: {task.due_date})" if task.due_date else ""
        print(f"  {status} [{task.priority.upper()}] {task.title}{due_date}")

    print()

    # Mark some tasks as completed
    print("Marking some tasks as completed...")
    manager.toggle_task_completion(task1.id)
    manager.toggle_task_completion(task3.id)

    # Show statistics
    stats = manager.get_statistics()
    print(f"\nStatistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Incomplete: {stats['incomplete']}")
    print(f"  High Priority: {stats['high_priority']}")
    print(f"  Medium Priority: {stats['medium_priority']}")
    print(f"  Low Priority: {stats['low_priority']}")

    # Search functionality
    print(f"\nSearching for 'python':")
    search_results = manager.search_tasks("python")
    for task in search_results:
        print(f"  - {task.title}")

    # Filter by status
    print(f"\nActive tasks:")
    active_tasks = manager.get_tasks_by_status(False)
    for task in active_tasks:
        print(f"  - {task.title}")

    print(f"\nCompleted tasks:")
    completed_tasks = manager.get_tasks_by_status(True)
    for task in completed_tasks:
        print(f"  - {task.title}")

    # Clean up
    manager.clear_completed_tasks()
    print(f"\nCleared completed tasks. Remaining: {len(manager.get_all_tasks())}")

    # Clean up demo file
    Path("demo_tasks.json").unlink(missing_ok=True)
    print("Demo completed successfully!")


def demo_gui():
    """Demonstrate GUI functionality."""
    print("\n=== To-Do GUI Application Demo ===")
    print("Starting GUI application...")
    print("You can now interact with the graphical interface!")
    print("Close the window to return to the command line.\n")

    from to_do_gui import TodoGUI

    # Create and run the GUI
    app = TodoGUI("demo_gui_tasks.json")
    app.run()

    # Clean up demo file
    Path("demo_gui_tasks.json").unlink(missing_ok=True)
    print("GUI demo completed!")


if __name__ == "__main__":
    print("To-Do GUI Application Demo")
    print("=" * 40)

    # Run core functionality demo
    demo_core_functionality()

    # Ask user if they want to see GUI demo
    try:
        response = input("\nWould you like to see the GUI demo? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            demo_gui()
        else:
            print("Skipping GUI demo.")
    except KeyboardInterrupt:
        print("\nDemo interrupted by user.")

    print("\nThank you for trying the To-Do GUI application!")
