#!/usr/bin/env python3

import unittest
import os
import tempfile
from to_do_list import TodoList


class TestTodoList(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_filename = self.temp_file.name
        self.temp_file.close()
        self.todo_list = TodoList(self.temp_filename)

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_filename):
            os.unlink(self.temp_filename)

    def test_add_task(self):
        """Test adding a new task."""
        result = self.todo_list.add_task("Test task", "high")
        self.assertTrue(result)
        self.assertEqual(len(self.todo_list.tasks), 1)

        task = self.todo_list.tasks[0]
        self.assertEqual(task["description"], "Test task")
        self.assertEqual(task["priority"], "high")
        self.assertFalse(task["completed"])
        self.assertIsNotNone(task["created_at"])

    def test_add_empty_task(self):
        """Test adding an empty task."""
        result = self.todo_list.add_task("", "medium")
        self.assertFalse(result)
        self.assertEqual(len(self.todo_list.tasks), 0)

        result = self.todo_list.add_task("   ", "medium")
        self.assertFalse(result)
        self.assertEqual(len(self.todo_list.tasks), 0)

    def test_mark_complete(self):
        """Test marking a task as complete."""
        self.todo_list.add_task("Test task")
        task_id = self.todo_list.tasks[0]["id"]

        result = self.todo_list.mark_complete(task_id)
        self.assertTrue(result)

        task = self.todo_list.tasks[0]
        self.assertTrue(task["completed"])
        self.assertIsNotNone(task["completed_at"])

    def test_mark_complete_nonexistent(self):
        """Test marking a non-existent task as complete."""
        result = self.todo_list.mark_complete(999)
        self.assertFalse(result)

    def test_mark_incomplete(self):
        """Test marking a task as incomplete."""
        self.todo_list.add_task("Test task")
        task_id = self.todo_list.tasks[0]["id"]

        # First mark as complete
        self.todo_list.mark_complete(task_id)

        # Then mark as incomplete
        result = self.todo_list.mark_incomplete(task_id)
        self.assertTrue(result)

        task = self.todo_list.tasks[0]
        self.assertFalse(task["completed"])
        self.assertIsNone(task["completed_at"])

    def test_delete_task(self):
        """Test deleting a task."""
        self.todo_list.add_task("Test task")
        task_id = self.todo_list.tasks[0]["id"]

        result = self.todo_list.delete_task(task_id)
        self.assertTrue(result)
        self.assertEqual(len(self.todo_list.tasks), 0)

    def test_delete_nonexistent_task(self):
        """Test deleting a non-existent task."""
        result = self.todo_list.delete_task(999)
        self.assertFalse(result)

    def test_get_tasks_all(self):
        """Test getting all tasks."""
        self.todo_list.add_task("Task 1")
        self.todo_list.add_task("Task 2")
        self.todo_list.mark_complete(self.todo_list.tasks[0]["id"])

        tasks = self.todo_list.get_tasks()
        self.assertEqual(len(tasks), 2)

    def test_get_tasks_pending_only(self):
        """Test getting only pending tasks."""
        self.todo_list.add_task("Task 1")
        self.todo_list.add_task("Task 2")
        self.todo_list.mark_complete(self.todo_list.tasks[0]["id"])

        tasks = self.todo_list.get_tasks(show_completed=False)
        self.assertEqual(len(tasks), 1)
        self.assertFalse(tasks[0]["completed"])

    def test_search_tasks(self):
        """Test searching tasks."""
        self.todo_list.add_task("Buy groceries")
        self.todo_list.add_task("Walk the dog")
        self.todo_list.add_task("Read a book")

        results = self.todo_list.search_tasks("book")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["description"], "Read a book")

        results = self.todo_list.search_tasks("the")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["description"], "Walk the dog")

    def test_get_stats(self):
        """Test getting task statistics."""
        # Empty list
        stats = self.todo_list.get_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["completed"], 0)
        self.assertEqual(stats["pending"], 0)

        # Add tasks
        self.todo_list.add_task("Task 1")
        self.todo_list.add_task("Task 2")
        self.todo_list.add_task("Task 3")

        stats = self.todo_list.get_stats()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["completed"], 0)
        self.assertEqual(stats["pending"], 3)

        # Complete one task
        self.todo_list.mark_complete(self.todo_list.tasks[0]["id"])

        stats = self.todo_list.get_stats()
        self.assertEqual(stats["total"], 3)
        self.assertEqual(stats["completed"], 1)
        self.assertEqual(stats["pending"], 2)

    def test_save_load_tasks(self):
        """Test saving and loading tasks."""
        # Add tasks
        self.todo_list.add_task("Task 1", "high")
        self.todo_list.add_task("Task 2", "low")
        self.todo_list.mark_complete(self.todo_list.tasks[0]["id"])

        # Create new instance to load from file
        new_todo_list = TodoList(self.temp_filename)

        self.assertEqual(len(new_todo_list.tasks), 2)
        self.assertEqual(new_todo_list.tasks[0]["description"], "Task 1")
        self.assertEqual(new_todo_list.tasks[0]["priority"], "high")
        self.assertTrue(new_todo_list.tasks[0]["completed"])

        self.assertEqual(new_todo_list.tasks[1]["description"], "Task 2")
        self.assertEqual(new_todo_list.tasks[1]["priority"], "low")
        self.assertFalse(new_todo_list.tasks[1]["completed"])


if __name__ == "__main__":
    unittest.main()
