
import pytest
from app.models import Task
from app.services.task_service import create_task, get_tasks, update_task

def test_create_task_with_category(user, app):
    """Test creating a task with a specific category."""
    with app.app_context():
        task = create_task(
            user_id=user.id,
            title="Category Task",
            category="Work"
        )
        assert task.category == "Work"
        assert task.title == "Category Task"

def test_create_task_default_category(user, app):
    """Test creating a task without a category defaults to 'General' (or None if not set in service, but route sets it)."""
    # Note: Service defaults to None if not provided, but route defaults to "General".
    # Here we test the service directly, so it might be None depending on implementation.
    # Let's check service implementation.
    # Service create_task signature: category: str | None = None
    with app.app_context():
        task = create_task(
            user_id=user.id,
            title="No Category Task"
        )
        assert task.category == "General"

def test_filter_tasks_by_category(user, app):
    """Test filtering tasks by category."""
    with app.app_context():
        create_task(user_id=user.id, title="Work Task", category="Work")
        create_task(user_id=user.id, title="Personal Task", category="Personal")
        create_task(user_id=user.id, title="Another Work Task", category="Work")

        tasks_work, _ = get_tasks(user_id=user.id, category="Work")
        assert len(tasks_work) == 2
        for t in tasks_work:
            assert t.category == "Work"

        tasks_personal, _ = get_tasks(user_id=user.id, category="Personal")
        assert len(tasks_personal) == 1
        assert tasks_personal[0].category == "Personal"

def test_update_task_category(user, app):
    """Test updating a task's category."""
    with app.app_context():
        task = create_task(user_id=user.id, title="Update Category Task", category="Old")
        updated_task = update_task(task.id, user.id, category="New")
        assert updated_task.category == "New"

def test_sort_tasks_by_category(user, app):
    """Test sorting tasks by category."""
    with app.app_context():
        create_task(user_id=user.id, title="C Task", category="C")
        create_task(user_id=user.id, title="A Task", category="A")
        create_task(user_id=user.id, title="B Task", category="B")

        tasks, _ = get_tasks(user_id=user.id, sort_by="category", order="asc")
        assert len(tasks) == 3
        assert tasks[0].category == "A"
        assert tasks[1].category == "B"
        assert tasks[2].category == "C"
