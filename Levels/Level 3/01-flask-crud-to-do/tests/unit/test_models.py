"""Unit tests for database models."""

import pytest
from werkzeug.security import check_password_hash

from app import db
from app.models.task import Task
from app.models.user import User


class TestUserModel:
    """Test User model."""

    def test_user_creation(self, app):
        """Test creating a user."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == "testuser"
            assert user.email == "test@example.com"
            assert user.password_hash is not None
            assert user.password_hash != "password123"

    def test_user_password_hashing(self, app):
        """Test password hashing."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")

            assert check_password_hash(user.password_hash, "password123")
            assert not check_password_hash(user.password_hash, "wrongpassword")

    def test_user_check_password(self, app):
        """Test password checking."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")

            assert user.check_password("password123") is True
            assert user.check_password("wrongpassword") is False

    def test_user_repr(self, app):
        """Test user string representation."""
        with app.app_context():
            user = User(username="testuser", email="test@example.com")
            assert "testuser" in repr(user)


class TestTaskModel:
    """Test Task model."""

    def test_task_creation(self, app, user):
        """Test creating a task."""
        with app.app_context():
            task = Task(title="Test Task", description="Test Description", user_id=user.id)
            db.session.add(task)
            db.session.commit()

            assert task.id is not None
            assert task.title == "Test Task"
            assert task.description == "Test Description"
            assert task.completed is False
            assert task.user_id == user.id

    def test_task_toggle_completion(self, app, task):
        """Test toggling task completion."""
        with app.app_context():
            initial_status = task.completed
            task.toggle_completed()

            assert task.completed != initial_status
            assert task.completed is True

            task.toggle_completed()
            assert task.completed is False

    def test_task_repr(self, app, task):
        """Test task string representation."""
        with app.app_context():
            assert "Test Task" in repr(task)

    def test_task_relationship(self, app, user):
        """Test task-user relationship."""
        with app.app_context():
            task = Task(title="Test Task", user_id=user.id)
            db.session.add(task)
            db.session.commit()

            refreshed_user = db.session.get(User, user.id)
            assert task.user == refreshed_user
            assert task in refreshed_user.tasks.all()
