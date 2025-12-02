"""Unit tests for authentication service."""

import pytest

from app import db
from app.models.user import User
from app.services.auth_service import authenticate_user, register_user
from app.utils.exceptions import ValidationError


class TestRegisterUser:
    """Test user registration."""

    def test_register_user_success(self, app):
        """Test successful user registration."""
        with app.app_context():
            user = register_user("newuser", "newuser@example.com", "password123")

            assert user.id is not None
            assert user.username == "newuser"
            assert user.email == "newuser@example.com"
            assert user.check_password("password123")

    def test_register_duplicate_username(self, app, user):
        """Test registration with duplicate username."""
        with app.app_context():
            with pytest.raises(ValidationError, match="already exists"):
                register_user(user.username, "different@example.com", "password123")

    def test_register_duplicate_email(self, app, user):
        """Test registration with duplicate email."""
        with app.app_context():
            with pytest.raises(ValidationError, match="already exists"):
                register_user("differentuser", user.email, "password123")


class TestAuthenticateUser:
    """Test user authentication."""

    def test_authenticate_success(self, app, user):
        """Test successful authentication."""
        with app.app_context():
            authenticated = authenticate_user("testuser", "testpass123")

            assert authenticated is not None
            assert authenticated.id == user.id
            assert authenticated.username == user.username

    def test_authenticate_wrong_password(self, app, user):
        """Test authentication with wrong password."""
        with app.app_context():
            authenticated = authenticate_user("testuser", "wrongpassword")

            assert authenticated is None

    def test_authenticate_nonexistent_user(self, app):
        """Test authentication with nonexistent user."""
        with app.app_context():
            authenticated = authenticate_user("nonexistent", "password123")

            assert authenticated is None
