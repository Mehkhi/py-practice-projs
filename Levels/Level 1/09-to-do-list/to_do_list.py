#!/usr/bin/env python3

import json
import os
from datetime import datetime
from typing import List, Dict, Any


class TodoList:
    """A simple to-do list manager with JSON persistence."""

    def __init__(self, filename="todos.json"):
        self.filename = filename
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Load tasks from JSON file."""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r', encoding='utf-8') as file:
                    self.tasks = json.load(file)
            else:
                self.tasks = []
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading tasks: {e}")
            self.tasks = []

    def save_tasks(self):
        """Save tasks to JSON file."""
        try:
            with open(self.filename, 'w', encoding='utf-8') as file:
                json.dump(self.tasks, file, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving tasks: {e}")

    def add_task(self, description: str, priority: str = "medium") -> bool:
        """Add a new task to the list."""
        if not description.strip():
            return False

        task = {
            "id": len(self.tasks) + 1,
            "description": description.strip(),
            "completed": False,
            "priority": priority.lower(),
            "created_at": datetime.now().isoformat(),
            "completed_at": None
        }

        self.tasks.append(task)
        self.save_tasks()
        return True

    def mark_complete(self, task_id: int) -> bool:
        """Mark a task as completed."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self.save_tasks()
                return True
        return False

    def mark_incomplete(self, task_id: int) -> bool:
        """Mark a task as incomplete."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = False
                task["completed_at"] = None
                self.save_tasks()
                return True
        return False

    def delete_task(self, task_id: int) -> bool:
        """Delete a task from the list."""
        for i, task in enumerate(self.tasks):
            if task["id"] == task_id:
                del self.tasks[i]
                self.save_tasks()
                return True
        return False

    def get_tasks(self, show_completed: bool = True) -> List[Dict[str, Any]]:
        """Get all tasks, optionally filtering by completion status."""
        if show_completed:
            return self.tasks
        else:
            return [task for task in self.tasks if not task["completed"]]

    def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        """Search tasks by description."""
        query = query.lower()
        return [task for task in self.tasks if query in task["description"].lower()]

    def get_stats(self) -> Dict[str, int]:
        """Get task statistics."""
        total = len(self.tasks)
        completed = len([task for task in self.tasks if task["completed"]])
        pending = total - completed

        return {
            "total": total,
            "completed": completed,
            "pending": pending
        }


def display_tasks(tasks: List[Dict[str, Any]], show_numbers: bool = True):
    """Display a list of tasks in a formatted way."""
    if not tasks:
        print("No tasks found.")
        return

    print("\n" + "="*60)
    print("[CLIPBOARD] TO-DO LIST")
    print("="*60)

    for i, task in enumerate(tasks, 1):
        status = "[OK]" if task["completed"] else "[O]"
        priority_emoji = {"high": "[RED CIRCLE]", "medium": "[YELLOW CIRCLE]", "low": "[GREEN CIRCLE]"}.get(task["priority"], "[WHITE CIRCLE]")

        if show_numbers:
            print(f"{i:2d}. {status} {priority_emoji} {task['description']}")
        else:
            print(f"    {status} {priority_emoji} {task['description']}")

        if task["completed"] and task["completed_at"]:
            completed_date = task["completed_at"][:10]  # Just the date part
            print(f"       Completed: {completed_date}")

    print("="*60)


def get_user_input(prompt: str, allow_empty: bool = False) -> str:
    """Get and validate user input."""
    while True:
        try:
            user_input = input(prompt).strip()
            if user_input or allow_empty:
                return user_input
            else:
                print("Please enter some text.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()
        except EOFError:
            print("\nGoodbye!")
            exit()


def get_task_id(todo_list: TodoList, prompt: str) -> int:
    """Get a valid task ID from user."""
    while True:
        try:
            task_id = int(input(prompt))
            if 1 <= task_id <= len(todo_list.tasks):
                return task_id
            else:
                print(f"Please enter a number between 1 and {len(todo_list.tasks)}.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            exit()
        except EOFError:
            print("\nGoodbye!")
            exit()


def add_task_menu(todo_list: TodoList):
    """Handle adding a new task."""
    print("\n=== Add New Task ===")
    description = get_user_input("Enter task description: ")

    print("\nPriority levels:")
    print("1. High")
    print("2. Medium")
    print("3. Low")

    priority_choice = input("Select priority (1-3, default=2): ").strip()
    priority_map = {"1": "high", "2": "medium", "3": "low"}
    priority = priority_map.get(priority_choice, "medium")

    if todo_list.add_task(description, priority):
        print(f"[OK] Task added: {description}")
    else:
        print("[X] Failed to add task.")


def list_tasks_menu(todo_list: TodoList):
    """Handle listing tasks."""
    print("\n=== List Tasks ===")
    print("1. All tasks")
    print("2. Pending tasks only")
    print("3. Completed tasks only")
    print("4. Search tasks")

    choice = input("Select option (1-4): ").strip()

    if choice == "1":
        tasks = todo_list.get_tasks()
        display_tasks(tasks)
    elif choice == "2":
        tasks = todo_list.get_tasks(show_completed=False)
        display_tasks(tasks)
    elif choice == "3":
        tasks = [task for task in todo_list.tasks if task["completed"]]
        display_tasks(tasks)
    elif choice == "4":
        query = get_user_input("Enter search term: ")
        tasks = todo_list.search_tasks(query)
        display_tasks(tasks)
    else:
        print("Invalid choice.")


def complete_task_menu(todo_list: TodoList):
    """Handle marking tasks as complete."""
    pending_tasks = [task for task in todo_list.tasks if not task["completed"]]

    if not pending_tasks:
        print("\nNo pending tasks to complete!")
        return

    print("\n=== Complete Task ===")
    display_tasks(pending_tasks)

    # Get the actual task ID from the user
    task_id = get_task_id(todo_list, "Enter task number to complete: ")

    if todo_list.mark_complete(task_id):
        task = next((t for t in todo_list.tasks if t["id"] == task_id), None)
        if task:
            print(f"[OK] Task completed: {task['description']}")
    else:
        print("[X] Task not found.")


def manage_task_menu(todo_list: TodoList):
    """Handle task management (uncomplete, delete)."""
    if not todo_list.tasks:
        print("\nNo tasks to manage!")
        return

    print("\n=== Manage Task ===")
    display_tasks(todo_list.tasks)

    task_id = get_task_id(todo_list, "Enter task number to manage: ")
    task = next((t for t in todo_list.tasks if t["id"] == task_id), None)

    if not task:
        print("[X] Task not found.")
        return

    print(f"\nSelected task: {task['description']}")
    print("1. Mark as incomplete")
    print("2. Delete task")
    print("3. Cancel")

    choice = input("Select action (1-3): ").strip()

    if choice == "1":
        if todo_list.mark_incomplete(task_id):
            print("[OK] Task marked as incomplete.")
    elif choice == "2":
        confirm = input(f"Delete '{task['description']}'? (y/n): ").strip().lower()
        if confirm in ['y', 'yes']:
            if todo_list.delete_task(task_id):
                print("[OK] Task deleted.")
            else:
                print("[X] Failed to delete task.")
    elif choice == "3":
        print("Cancelled.")
    else:
        print("Invalid choice.")


def show_stats(todo_list: TodoList):
    """Display task statistics."""
    stats = todo_list.get_stats()

    print("\n" + "="*40)
    print("[BAR CHART] TASK STATISTICS")
    print("="*40)
    print(f"Total tasks:     {stats['total']}")
    print(f"Completed:       {stats['completed']}")
    print(f"Pending:         {stats['pending']}")

    if stats['total'] > 0:
        completion_rate = (stats['completed'] / stats['total']) * 100
        print(f"Completion rate: {completion_rate:.1f}%")

    print("="*40)


def display_menu():
    """Display the main menu."""
    print("\n" + "="*40)
    print("[MEMO] TO-DO LIST MANAGER")
    print("="*40)
    print("1. Add new task")
    print("2. List tasks")
    print("3. Complete task")
    print("4. Manage task")
    print("5. Show statistics")
    print("6. Exit")
    print("="*40)


def main():
    """Main function to run the to-do list manager."""
    todo_list = TodoList()

    print("Welcome to the To-Do List Manager!")

    while True:
        display_menu()

        try:
            choice = input("Enter your choice (1-6): ").strip()

            if choice == '1':
                add_task_menu(todo_list)
            elif choice == '2':
                list_tasks_menu(todo_list)
            elif choice == '3':
                complete_task_menu(todo_list)
            elif choice == '4':
                manage_task_menu(todo_list)
            elif choice == '5':
                show_stats(todo_list)
            elif choice == '6':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-6.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break


if __name__ == "__main__":
    main()
