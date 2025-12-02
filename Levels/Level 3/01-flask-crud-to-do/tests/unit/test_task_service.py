"""Unit tests for task service."""

import pytest

from app import db
from app.models.task import Task
from app.services.task_service import (
    add_dependency,
    add_note,
    change_status,
    create_task,
    delete_task,
    get_task,
    get_tasks,
    start_timer,
    stop_timer,
    toggle_task_completion,
    update_task,
)
from app.utils.exceptions import TaskAccessDeniedError, TaskNotFoundError


class TestCreateTask:
    """Test task creation."""

    def test_create_task_success(self, app, user):
        """Test successful task creation."""
        with app.app_context():
            task = create_task(user.id, "New Task", "Task Description")

            assert task.id is not None
            assert task.title == "New Task"
            assert task.description == "Task Description"
            assert task.user_id == user.id
            assert task.completed is False

    def test_create_task_minimal(self, app, user):
        """Test creating task with minimal data."""
        with app.app_context():
            task = create_task(user.id, "Minimal Task")

            assert task.title == "Minimal Task"
            assert task.description is None


class TestGetTask:
    """Test getting a task."""

    def test_get_task_success(self, app, task, user):
        """Test successfully getting a task."""
        with app.app_context():
            retrieved = get_task(task.id, user.id)

            assert retrieved.id == task.id
            assert retrieved.title == task.title

    def test_get_task_not_found(self, app, user):
        """Test getting nonexistent task."""
        with app.app_context():
            with pytest.raises(TaskNotFoundError):
                get_task(99999, user.id)

    def test_get_task_access_denied(self, app, task, another_user):
        """Test getting task owned by another user."""
        with app.app_context():
            with pytest.raises(TaskAccessDeniedError):
                get_task(task.id, another_user.id)


class TestGetTasks:
    """Test getting multiple tasks."""

    def test_get_all_tasks(self, app, user):
        """Test getting all tasks for a user."""
        with app.app_context():
            create_task(user.id, "Task 1")
            create_task(user.id, "Task 2")
            create_task(user.id, "Task 3")

            tasks, total = get_tasks(user.id)

            assert len(tasks) == 3
            assert total == 3

    def test_get_tasks_filter_completed(self, app, user):
        """Test filtering tasks by completion status."""
        with app.app_context():
            task1 = create_task(user.id, "Task 1")
            task2 = create_task(user.id, "Task 2")
            toggle_task_completion(task2.id, user.id)

            completed_tasks, _ = get_tasks(user.id, completed=True)
            incomplete_tasks, _ = get_tasks(user.id, completed=False)

            assert len(completed_tasks) == 1
            assert len(incomplete_tasks) == 1
            assert completed_tasks[0].id == task2.id
            assert incomplete_tasks[0].id == task1.id

    def test_get_tasks_search(self, app, user):
        """Test searching tasks."""
        with app.app_context():
            create_task(user.id, "Python Task", "Learn Python")
            create_task(user.id, "Flask Task", "Build Flask app")
            create_task(user.id, "Django Task", "Learn Django")

            tasks, _ = get_tasks(user.id, search="Python")

            assert len(tasks) == 1
            assert "Python" in tasks[0].title

    def test_get_tasks_pagination(self, app, user):
        """Test pagination."""
        with app.app_context():
            for i in range(15):
                create_task(user.id, f"Task {i}")

            page1, total = get_tasks(user.id, page=1, per_page=10)
            page2, _ = get_tasks(user.id, page=2, per_page=10)

            assert len(page1) == 10
            assert len(page2) == 5
            assert total == 15


class TestUpdateTask:
    """Test updating tasks."""

    def test_update_task_success(self, app, task, user):
        """Test successful task update."""
        with app.app_context():
            updated = update_task(task.id, user.id, title="Updated Title", description="Updated Desc")

            assert updated.title == "Updated Title"
            assert updated.description == "Updated Desc"

    def test_update_task_partial(self, app, task, user):
        """Test partial task update."""
        with app.app_context():
            original_desc = task.description
            updated = update_task(task.id, user.id, title="New Title")

            assert updated.title == "New Title"
            assert updated.description == original_desc


class TestDeleteTask:
    """Test deleting tasks."""

    def test_delete_task_success(self, app, task, user):
        """Test successful task deletion."""
        with app.app_context():
            task_id = task.id
            delete_task(task_id, user.id)

            assert Task.query.get(task_id) is None


class TestToggleTaskCompletion:
    """Test toggling task completion."""

    def test_toggle_task_completion(self, app, task, user):
        """Test toggling task completion status."""
        with app.app_context():
            initial_status = task.completed
            toggled = toggle_task_completion(task.id, user.id)

            assert toggled.completed != initial_status


class TestAdvancedFlows:
    """Test advanced workflow helpers."""

    def test_change_status_requires_approval(self, app, user):
        """Ensure approval gate is enforced."""
        with app.app_context():
            task = create_task(user.id, "Approval needed", requires_approval=True)
            with pytest.raises(TaskAccessDeniedError):
                change_status(task.id, user.id, "done")

    def test_dependency_cycle_blocked(self, app, user):
        """Prevent cycles when adding dependencies."""
        with app.app_context():
            t1 = create_task(user.id, "Task 1")
            t2 = create_task(user.id, "Task 2")
            add_dependency(t2.id, t1.id, user.id)
            with pytest.raises(ValueError):
                add_dependency(t1.id, t2.id, user.id)

    def test_start_stop_timer(self, app, user):
        """Start and stop timer logs duration."""
        with app.app_context():
            task = create_task(user.id, "Timed Task")
            start_timer(task.id, user.id)
            entry = stop_timer(task.id, user.id)
            assert entry is not None
            assert entry.duration_minutes >= 1

    def test_add_note(self, app, user):
        """Attach a note to a task."""
        with app.app_context():
            task = create_task(user.id, "Noted Task")
            note = add_note(task.id, user.id, "Remember to test", kind="acceptance")
            assert note.content == "Remember to test"
