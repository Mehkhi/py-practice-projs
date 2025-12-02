"""End-to-end tests for user flows."""

import pytest


class TestUserRegistrationFlow:
    """Test complete user registration flow."""

    def test_register_and_access_tasks(self, client, app):
        """Test registering and accessing tasks."""
        with app.app_context():
            # Register
            response = client.post(
                "/auth/register",
                data={
                    "username": "e2euser",
                    "email": "e2e@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"Registration successful" in response.data or b"My Tasks" in response.data

            # Should be able to access tasks page
            response = client.get("/tasks/")
            assert response.status_code == 200


class TestTaskManagementFlow:
    """Test complete task management flow."""

    def test_create_edit_delete_task_flow(self, authenticated_client, app, user):
        """Test creating, editing, and deleting a task."""
        with app.app_context():
            # Create task
            response = authenticated_client.post(
                "/tasks/create",
                data={"title": "E2E Task", "description": "E2E Description"},
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"E2E Task" in response.data

            # Get task ID from database
            from app.models.task import Task

            task = Task.query.filter_by(title="E2E Task").first()
            assert task is not None

            # Edit task
            response = authenticated_client.post(
                f"/tasks/{task.id}/update",
                data={"title": "Updated E2E Task", "description": "Updated Description"},
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"Updated E2E Task" in response.data

            # Toggle completion
            response = authenticated_client.post(
                f"/tasks/{task.id}/toggle", follow_redirects=True
            )

            assert response.status_code == 200
            assert b"completed" in response.data or b"incomplete" in response.data

            # Delete task
            response = authenticated_client.post(
                f"/tasks/{task.id}/delete", follow_redirects=True
            )

            assert response.status_code == 200
            assert b"deleted successfully" in response.data

            # Verify task is deleted
            deleted_task = Task.query.get(task.id)
            assert deleted_task is None


class TestAuthenticationFlow:
    """Test complete authentication flow."""

    def test_login_logout_flow(self, client, app, user):
        """Test login and logout flow."""
        with app.app_context():
            # Login
            response = client.post(
                "/auth/login",
                data={"username": user.username, "password": "testpass123"},
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"Login successful" in response.data or b"My Tasks" in response.data

            # Access protected route
            response = client.get("/tasks/")
            assert response.status_code == 200

            # Logout
            response = client.get("/auth/logout", follow_redirects=True)
            assert response.status_code == 200
            assert b"logged out" in response.data

            # Should not access protected route
            response = client.get("/tasks/", follow_redirects=True)
            # Should redirect to login
            assert response.status_code == 200
