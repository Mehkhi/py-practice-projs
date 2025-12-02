"""
Core functionality for the To-Do GUI application.

This module contains the Task class and TaskManager class that handle
the business logic for managing to-do items.
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Task:
    """Represents a single to-do task."""

    id: str
    title: str
    description: str = ""
    completed: bool = False
    priority: str = "medium"  # low, medium, high
    due_date: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""

    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.updated_at:
            self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """Create task from dictionary."""
        return cls(**data)

    def mark_completed(self) -> None:
        """Mark task as completed."""
        self.completed = True
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Task '{self.title}' marked as completed")

    def mark_incomplete(self) -> None:
        """Mark task as incomplete."""
        self.completed = False
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Task '{self.title}' marked as incomplete")

    def update(self, **kwargs) -> None:
        """Update task properties."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now().isoformat()
        logger.info(f"Task '{self.title}' updated")


class TaskManager:
    """Manages a collection of tasks with persistence."""

    def __init__(self, data_file: str = "tasks.json"):
        """Initialize task manager with data file path."""
        self.data_file = Path(data_file)
        self.tasks: Dict[str, Task] = {}
        self._next_id = 1
        self.load_tasks()

    def add_task(self, title: str, description: str = "", priority: str = "medium",
                 due_date: Optional[str] = None) -> Task:
        """Add a new task to the manager."""
        if not title.strip():
            raise ValueError("Task title cannot be empty")

        task_id = str(self._next_id)
        self._next_id += 1

        task = Task(
            id=task_id,
            title=title.strip(),
            description=description.strip(),
            priority=priority,
            due_date=due_date
        )

        self.tasks[task_id] = task
        self.save_tasks()
        logger.info(f"Added new task: '{title}'")
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks as a list."""
        return list(self.tasks.values())

    def get_tasks_by_status(self, completed: bool) -> List[Task]:
        """Get tasks filtered by completion status."""
        return [task for task in self.tasks.values() if task.completed == completed]

    def get_tasks_by_priority(self, priority: str) -> List[Task]:
        """Get tasks filtered by priority."""
        return [task for task in self.tasks.values() if task.priority == priority]

    def search_tasks(self, query: str) -> List[Task]:
        """Search tasks by title or description."""
        query = query.lower().strip()
        if not query:
            return self.get_all_tasks()

        results = []
        for task in self.tasks.values():
            if (query in task.title.lower() or
                query in task.description.lower()):
                results.append(task)
        return results

    def update_task(self, task_id: str, **kwargs) -> bool:
        """Update a task's properties."""
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"Task with ID {task_id} not found")
            return False

        try:
            task.update(**kwargs)
            self.save_tasks()
            return True
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            return False

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        if task_id not in self.tasks:
            logger.warning(f"Task with ID {task_id} not found")
            return False

        task_title = self.tasks[task_id].title
        del self.tasks[task_id]
        self.save_tasks()
        logger.info(f"Deleted task: '{task_title}'")
        return True

    def toggle_task_completion(self, task_id: str) -> bool:
        """Toggle task completion status."""
        task = self.get_task(task_id)
        if not task:
            logger.warning(f"Task with ID {task_id} not found")
            return False

        if task.completed:
            task.mark_incomplete()
        else:
            task.mark_completed()

        self.save_tasks()
        return True

    def save_tasks(self) -> None:
        """Save tasks to JSON file."""
        try:
            data = {
                "tasks": {task_id: task.to_dict() for task_id, task in self.tasks.items()},
                "next_id": self._next_id
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self.tasks)} tasks to {self.data_file}")
        except Exception as e:
            logger.error(f"Error saving tasks: {e}")
            raise

    def load_tasks(self) -> None:
        """Load tasks from JSON file."""
        if not self.data_file.exists():
            logger.info(f"Data file {self.data_file} does not exist, starting with empty task list")
            return

        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.tasks = {}
            for task_id, task_data in data.get("tasks", {}).items():
                self.tasks[task_id] = Task.from_dict(task_data)

            self._next_id = data.get("next_id", 1)
            logger.info(f"Loaded {len(self.tasks)} tasks from {self.data_file}")
        except Exception as e:
            logger.error(f"Error loading tasks: {e}")
            # Start with empty task list if loading fails
            self.tasks = {}
            self._next_id = 1

    def clear_completed_tasks(self) -> int:
        """Remove all completed tasks."""
        completed_tasks = self.get_tasks_by_status(True)
        count = len(completed_tasks)

        for task in completed_tasks:
            del self.tasks[task.id]

        if count > 0:
            self.save_tasks()
            logger.info(f"Cleared {count} completed tasks")

        return count

    def get_statistics(self) -> Dict[str, int]:
        """Get task statistics."""
        total = len(self.tasks)
        completed = len(self.get_tasks_by_status(True))
        incomplete = total - completed

        return {
            "total": total,
            "completed": completed,
            "incomplete": incomplete,
            "high_priority": len(self.get_tasks_by_priority("high")),
            "medium_priority": len(self.get_tasks_by_priority("medium")),
            "low_priority": len(self.get_tasks_by_priority("low"))
        }

    def get_filtered_tasks(self, filter_value: str = "all", search_query: str = "") -> List[Task]:
        """Return tasks filtered by status and search query."""
        tasks = self.get_all_tasks()

        if filter_value == "active":
            tasks = [task for task in tasks if not task.completed]
        elif filter_value == "completed":
            tasks = [task for task in tasks if task.completed]

        search_query = search_query.strip()
        if search_query:
            lowered_query = search_query.lower()
            tasks = [
                task for task in tasks
                if lowered_query in task.title.lower()
                or lowered_query in task.description.lower()
            ]

        return tasks
