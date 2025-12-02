"""Pytest configuration and fixtures."""

import os
import tempfile
from typing import Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app, db
from app.models.task import Task
from app.models.user import User


@pytest.fixture
def app() -> Generator[Flask, None, None]:
    """Create application for testing."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["SECRET_KEY"] = "test-secret-key"
    os.environ["FLASK_ENV"] = "testing"

    app = create_app("testing")
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create test client."""
    return app.test_client()


@pytest.fixture
def user(app: Flask) -> User:
    """Create a test user."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def authenticated_client(client: FlaskClient, app: Flask, user: User) -> FlaskClient:
    """Create authenticated test client."""
    with client:
        with client.session_transaction() as sess:
            sess["_user_id"] = str(user.id)
    return client


@pytest.fixture
def task(app: Flask, user: User) -> Task:
    """Create a test task."""
    with app.app_context():
        task = Task(title="Test Task", description="Test Description", user_id=user.id)
        db.session.add(task)
        db.session.commit()
        return task


@pytest.fixture
def another_user(app: Flask) -> User:
    """Create another test user."""
    with app.app_context():
        user = User(username="otheruser", email="other@example.com")
        user.set_password("testpass123")
        db.session.add(user)
        db.session.commit()
        return user
