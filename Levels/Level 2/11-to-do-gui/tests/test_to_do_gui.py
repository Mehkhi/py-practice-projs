"""
Comprehensive unit tests for the To-Do GUI application.

This module contains tests for all core functionality including
task management, persistence, validation, and edge cases.
"""

import pytest
import json
import tempfile
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from to_do_gui.core import Task, TaskManager


class TestTask:
    """Test cases for the Task class."""

    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(
            id="1",
            title="Test Task",
            description="Test Description",
            priority="high"
        )

        assert task.id == "1"
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == "high"
        assert task.completed is False
        assert task.created_at != ""
        assert task.updated_at != ""

    def test_task_creation_with_timestamps(self):
        """Test task creation with provided timestamps."""
        created = "2023-01-01T10:00:00"
        updated = "2023-01-01T11:00:00"

        task = Task(
            id="1",
            title="Test Task",
            created_at=created,
            updated_at=updated
        )

        assert task.created_at == created
        assert task.updated_at == updated

    def test_task_mark_completed(self):
        """Test marking task as completed."""
        task = Task(id="1", title="Test Task")
        assert not task.completed

        task.mark_completed()
        assert task.completed
        assert task.updated_at != ""

    def test_task_mark_incomplete(self):
        """Test marking task as incomplete."""
        task = Task(id="1", title="Test Task", completed=True)
        assert task.completed

        task.mark_incomplete()
        assert not task.completed
        assert task.updated_at != ""

    def test_task_update(self):
        """Test updating task properties."""
        task = Task(id="1", title="Original Title")
        original_updated = task.updated_at

        task.update(title="Updated Title", priority="high")

        assert task.title == "Updated Title"
        assert task.priority == "high"
        assert task.updated_at != original_updated

    def test_task_to_dict(self):
        """Test converting task to dictionary."""
        task = Task(
            id="1",
            title="Test Task",
            description="Test Description",
            priority="medium",
            completed=True
        )

        task_dict = task.to_dict()

        assert task_dict["id"] == "1"
        assert task_dict["title"] == "Test Task"
        assert task_dict["description"] == "Test Description"
        assert task_dict["priority"] == "medium"
        assert task_dict["completed"] is True

    def test_task_from_dict(self):
        """Test creating task from dictionary."""
        task_data = {
            "id": "1",
            "title": "Test Task",
            "description": "Test Description",
            "priority": "low",
            "completed": False,
            "due_date": "2023-12-31",
            "created_at": "2023-01-01T10:00:00",
            "updated_at": "2023-01-01T11:00:00"
        }

        task = Task.from_dict(task_data)

        assert task.id == "1"
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == "low"
        assert task.completed is False
        assert task.due_date == "2023-12-31"
        assert task.created_at == "2023-01-01T10:00:00"
        assert task.updated_at == "2023-01-01T11:00:00"


class TestTaskManager:
    """Test cases for the TaskManager class."""

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('{"tasks": {}, "next_id": 1}')
        yield f.name
        os.unlink(f.name)

    @pytest.fixture
    def task_manager(self, temp_file):
        """Create a TaskManager instance with temporary file."""
        return TaskManager(temp_file)

    def test_task_manager_initialization(self, temp_file):
        """Test TaskManager initialization."""
        manager = TaskManager(temp_file)
        assert manager.data_file == Path(temp_file)
        assert len(manager.tasks) == 0
        assert manager._next_id == 1

    def test_add_task_success(self, task_manager):
        """Test successful task addition."""
        task = task_manager.add_task("Test Task", "Test Description", "high")

        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.priority == "high"
        assert task.id == "1"
        assert len(task_manager.tasks) == 1
        assert "1" in task_manager.tasks

    def test_add_task_empty_title(self, task_manager):
        """Test adding task with empty title raises error."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            task_manager.add_task("")

        with pytest.raises(ValueError, match="Task title cannot be empty"):
            task_manager.add_task("   ")

    def test_add_task_with_due_date(self, task_manager):
        """Test adding task with due date."""
        task = task_manager.add_task(
            "Test Task",
            due_date="2023-12-31"
        )

        assert task.due_date == "2023-12-31"

    def test_get_task_existing(self, task_manager):
        """Test getting existing task."""
        task_manager.add_task("Test Task")
        retrieved_task = task_manager.get_task("1")

        assert retrieved_task is not None
        assert retrieved_task.title == "Test Task"

    def test_get_task_nonexistent(self, task_manager):
        """Test getting non-existent task."""
        retrieved_task = task_manager.get_task("999")
        assert retrieved_task is None

    def test_get_all_tasks(self, task_manager):
        """Test getting all tasks."""
        task_manager.add_task("Task 1")
        task_manager.add_task("Task 2")

        all_tasks = task_manager.get_all_tasks()
        assert len(all_tasks) == 2
        assert all(isinstance(task, Task) for task in all_tasks)

    def test_get_tasks_by_status(self, task_manager):
        """Test getting tasks by completion status."""
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task2.mark_completed()

        completed_tasks = task_manager.get_tasks_by_status(True)
        incomplete_tasks = task_manager.get_tasks_by_status(False)

        assert len(completed_tasks) == 1
        assert len(incomplete_tasks) == 1
        assert completed_tasks[0].id == task2.id
        assert incomplete_tasks[0].id == task1.id

    def test_get_tasks_by_priority(self, task_manager):
        """Test getting tasks by priority."""
        task_manager.add_task("High Task", priority="high")
        task_manager.add_task("Medium Task", priority="medium")
        task_manager.add_task("Low Task", priority="low")

        high_tasks = task_manager.get_tasks_by_priority("high")
        medium_tasks = task_manager.get_tasks_by_priority("medium")
        low_tasks = task_manager.get_tasks_by_priority("low")

        assert len(high_tasks) == 1
        assert len(medium_tasks) == 1
        assert len(low_tasks) == 1
        assert high_tasks[0].title == "High Task"
        assert medium_tasks[0].title == "Medium Task"
        assert low_tasks[0].title == "Low Task"

    def test_search_tasks(self, task_manager):
        """Test searching tasks."""
        task_manager.add_task("Python Programming", "Learn Python basics")
        task_manager.add_task("JavaScript Course", "Advanced JS concepts")
        task_manager.add_task("Data Science", "Python for data analysis")

        # Search by title
        python_tasks = task_manager.search_tasks("Python")
        assert len(python_tasks) == 2

        # Search by description
        js_tasks = task_manager.search_tasks("JS")
        assert len(js_tasks) == 1

        # Empty search returns all tasks
        all_tasks = task_manager.search_tasks("")
        assert len(all_tasks) == 3

    def test_get_filtered_tasks_with_search_and_status(self, task_manager):
        """Search results should respect status filters."""
        task_manager.add_task("Write report", "Finish quarterly report")
        task_manager.add_task("Review PR", "Code review for feature")
        task_manager.add_task("Read book", "Book review notes")

        # Mark second task as completed
        task_manager.toggle_task_completion("2")

        active_results = task_manager.get_filtered_tasks("active", "re")
        completed_results = task_manager.get_filtered_tasks("completed", "RE")

        assert {task.id for task in active_results} == {"1", "3"}
        assert {task.id for task in completed_results} == {"2"}

    def test_update_task_success(self, task_manager):
        """Test successful task update."""
        task_manager.add_task("Original Title")

        success = task_manager.update_task("1", title="Updated Title", priority="high")

        assert success is True
        updated_task = task_manager.get_task("1")
        assert updated_task.title == "Updated Title"
        assert updated_task.priority == "high"

    def test_update_task_nonexistent(self, task_manager):
        """Test updating non-existent task."""
        success = task_manager.update_task("999", title="New Title")
        assert success is False

    def test_delete_task_success(self, task_manager):
        """Test successful task deletion."""
        task_manager.add_task("Test Task")
        assert len(task_manager.tasks) == 1

        success = task_manager.delete_task("1")

        assert success is True
        assert len(task_manager.tasks) == 0
        assert task_manager.get_task("1") is None

    def test_delete_task_nonexistent(self, task_manager):
        """Test deleting non-existent task."""
        success = task_manager.delete_task("999")
        assert success is False

    def test_toggle_task_completion(self, task_manager):
        """Test toggling task completion status."""
        task_manager.add_task("Test Task")
        task = task_manager.get_task("1")
        assert not task.completed

        # Toggle to completed
        success = task_manager.toggle_task_completion("1")
        assert success is True
        assert task_manager.get_task("1").completed is True

        # Toggle back to incomplete
        success = task_manager.toggle_task_completion("1")
        assert success is True
        assert task_manager.get_task("1").completed is False

    def test_toggle_task_nonexistent(self, task_manager):
        """Test toggling non-existent task."""
        success = task_manager.toggle_task_completion("999")
        assert success is False

    def test_clear_completed_tasks(self, task_manager):
        """Test clearing completed tasks."""
        task1 = task_manager.add_task("Task 1")
        task2 = task_manager.add_task("Task 2")
        task3 = task_manager.add_task("Task 3")

        task2.mark_completed()
        task3.mark_completed()

        cleared_count = task_manager.clear_completed_tasks()

        assert cleared_count == 2
        assert len(task_manager.tasks) == 1
        assert task_manager.get_task("1") is not None
        assert task_manager.get_task("2") is None
        assert task_manager.get_task("3") is None

    def test_get_statistics(self, task_manager):
        """Test getting task statistics."""
        task_manager.add_task("High Task", priority="high")
        task_manager.add_task("Medium Task", priority="medium")
        task_manager.add_task("Low Task", priority="low")

        # Mark one task as completed
        task_manager.toggle_task_completion("1")

        stats = task_manager.get_statistics()

        assert stats["total"] == 3
        assert stats["completed"] == 1
        assert stats["incomplete"] == 2
        assert stats["high_priority"] == 1
        assert stats["medium_priority"] == 1
        assert stats["low_priority"] == 1

    def test_save_and_load_tasks(self, temp_file):
        """Test saving and loading tasks from file."""
        # Create manager and add tasks
        manager1 = TaskManager(temp_file)
        manager1.add_task("Task 1", priority="high")
        manager1.add_task("Task 2", priority="low")
        manager1.toggle_task_completion("1")

        # Create new manager and load tasks
        manager2 = TaskManager(temp_file)

        assert len(manager2.tasks) == 2
        assert manager2.get_task("1").title == "Task 1"
        assert manager2.get_task("1").completed is True
        assert manager2.get_task("2").title == "Task 2"
        assert manager2.get_task("2").completed is False
        assert manager2._next_id == 3

    def test_load_tasks_file_not_exists(self):
        """Test loading tasks when file doesn't exist."""
        manager = TaskManager("nonexistent_file.json")
        assert len(manager.tasks) == 0
        assert manager._next_id == 1

    def test_save_tasks_error_handling(self, task_manager):
        """Test error handling during task saving."""
        # Mock file operations to raise an error
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with pytest.raises(IOError):
                task_manager.save_tasks()

    def test_load_tasks_error_handling(self):
        """Test error handling during task loading."""
        # Create a file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            f.write('invalid json content')

        try:
            manager = TaskManager(f.name)
            # Should not raise exception, but start with empty task list
            assert len(manager.tasks) == 0
            assert manager._next_id == 1
        finally:
            os.unlink(f.name)


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_task_with_special_characters(self):
        """Test task with special characters in title and description."""
        task = Task(
            id="1",
            title="Task with émojis 🎯 and spëcial chars",
            description="Description with unicode: αβγδε and symbols: @#$%"
        )

        assert task.title == "Task with émojis 🎯 and spëcial chars"
        assert task.description == "Description with unicode: αβγδε and symbols: @#$%"

    def test_task_with_very_long_text(self):
        """Test task with very long text."""
        long_title = "A" * 1000
        long_description = "B" * 5000

        task = Task(
            id="1",
            title=long_title,
            description=long_description
        )

        assert len(task.title) == 1000
        assert len(task.description) == 5000

    def test_task_priority_case_insensitive(self):
        """Test that priority handling is case sensitive as expected."""
        task = Task(id="1", title="Test", priority="HIGH")
        assert task.priority == "HIGH"  # Should preserve case

    def test_task_due_date_edge_cases(self):
        """Test due date edge cases."""
        # Valid dates
        task1 = Task(id="1", title="Test", due_date="2023-12-31")
        task2 = Task(id="2", title="Test", due_date="2024-02-29")  # Leap year

        assert task1.due_date == "2023-12-31"
        assert task2.due_date == "2024-02-29"

        # Empty due date
        task3 = Task(id="3", title="Test", due_date="")
        assert task3.due_date == ""

        # None due date
        task4 = Task(id="4", title="Test", due_date=None)
        assert task4.due_date is None


if __name__ == "__main__":
    pytest.main([__file__])
