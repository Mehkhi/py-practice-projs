"""Integration tests for task routes."""

import pytest
from flask import url_for


class TestTaskListRoute:
    """Test task list route."""

    def test_list_tasks_requires_login(self, client):
        """Test task list requires authentication."""
        response = client.get("/tasks/", follow_redirects=True)
        assert response.status_code == 200

    def test_list_tasks_success(self, authenticated_client, app, user):
        """Test successful task listing."""
        with app.app_context():
            from app.services.task_service import create_task

            create_task(user.id, "Task 1")
            create_task(user.id, "Task 2")

            response = authenticated_client.get("/tasks/")
            assert response.status_code == 200
            assert b"Task 1" in response.data
            assert b"Task 2" in response.data

    def test_list_tasks_filtering(self, authenticated_client, app, user):
        """Test task filtering."""
        with app.app_context():
            from app.services.task_service import create_task, toggle_task_completion

            task1 = create_task(user.id, "Incomplete Task")
            task2 = create_task(user.id, "Complete Task")
            toggle_task_completion(task2.id, user.id)

            response = authenticated_client.get("/tasks/?completed=false")
            assert response.status_code == 200
            assert b"Incomplete Task" in response.data

            response = authenticated_client.get("/tasks/?completed=true")
            assert response.status_code == 200
            assert b"Complete Task" in response.data


class TestCreateTaskRoute:
    """Test task creation route."""

    def test_create_task_get(self, authenticated_client):
        """Test GET create task page."""
        response = authenticated_client.get("/tasks/new")
        assert response.status_code == 200
        assert b"New Task" in response.data

    def test_create_task_post_success(self, authenticated_client, app, user):
        """Test successful task creation."""
        with app.app_context():
            response = authenticated_client.post(
                "/tasks/create",
                data={"title": "New Task", "description": "Task Description"},
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"created" in response.data
            assert b"New Task" in response.data

    def test_create_task_missing_title(self, authenticated_client):
        """Test task creation without title."""
        response = authenticated_client.post("/tasks/create", data={"description": "Desc"})
        assert response.status_code == 302  # Redirect back


class TestUpdateTaskRoute:
    """Test task update route."""

    def test_update_task_get(self, authenticated_client, app, task, user):
        """Test GET edit task page."""
        with app.app_context():
            response = authenticated_client.get(f"/tasks/{task.id}/edit")
            assert response.status_code == 200
            assert b"Update Task" in response.data
            assert task.title.encode() in response.data

    def test_update_task_post_success(self, authenticated_client, app, task, user):
        """Test successful task update."""
        with app.app_context():
            response = authenticated_client.post(
                f"/tasks/{task.id}/update",
                data={"title": "Updated Task", "description": "Updated Description"},
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"updated successfully" in response.data

    def test_update_task_access_denied(self, authenticated_client, app, task, another_user):
        """Test updating task owned by another user."""
        with app.app_context():
            # Impersonate different user to validate access guard
            with authenticated_client.session_transaction() as sess:
                sess["_user_id"] = str(another_user.id)
            response = authenticated_client.get(f"/tasks/{task.id}/edit", follow_redirects=True)
            assert response.status_code == 200
            assert b"permission" in response.data or b"not found" in response.data


class TestDeleteTaskRoute:
    """Test task deletion route."""

    def test_delete_task_success(self, authenticated_client, app, user):
        """Test successful task deletion."""
        with app.app_context():
            from app.services.task_service import create_task

            task = create_task(user.id, "Task to Delete")

            response = authenticated_client.post(
                f"/tasks/{task.id}/delete", follow_redirects=True
            )
            assert response.status_code == 200
            assert b"deleted successfully" in response.data


class TestToggleTaskRoute:
    """Test task toggle route."""

    def test_toggle_task_success(self, authenticated_client, app, task, user):
        """Test successful task toggle."""
        with app.app_context():
            initial_status = task.completed

            response = authenticated_client.post(
                f"/tasks/{task.id}/toggle", follow_redirects=True
            )

            assert response.status_code == 200
            # Check that status changed
            from app.models.task import Task

            updated_task = Task.query.get(task.id)
            assert updated_task.completed != initial_status


class TestAdvancedTaskViews:
    """Test advanced kanban/detail/template views."""

    def test_board_view(self, authenticated_client, app, user):
        with app.app_context():
            from app.services.task_service import create_task

            create_task(user.id, "Board Task")
            response = authenticated_client.get("/tasks/board")
            assert response.status_code == 200
            assert b"Kanban" in response.data

    def test_templates_view(self, authenticated_client):
        response = authenticated_client.get("/tasks/templates")
        assert response.status_code == 200
        assert b"Templates" in response.data

    def test_task_detail_view(self, authenticated_client, task):
        response = authenticated_client.get(f"/tasks/{task.id}")
        assert response.status_code == 200
        assert task.title.encode() in response.data
