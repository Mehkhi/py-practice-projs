"""Integration tests for authentication routes."""

import pytest
from flask import url_for


class TestRegisterRoute:
    """Test registration route."""

    def test_register_get(self, client):
        """Test GET registration page."""
        response = client.get("/auth/register")
        assert response.status_code == 200
        assert b"Register" in response.data

    def test_register_post_success(self, client, app):
        """Test successful registration."""
        with app.app_context():
            response = client.post(
                "/auth/register",
                data={
                    "username": "newuser",
                    "email": "newuser@example.com",
                    "password": "password123",
                },
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"Registration successful" in response.data or b"My Tasks" in response.data

    def test_register_duplicate_username(self, client, app, user):
        """Test registration with duplicate username."""
        with app.app_context():
            response = client.post(
                "/auth/register",
                data={
                    "username": user.username,
                    "email": "different@example.com",
                    "password": "password123",
                },
            )

            assert response.status_code == 200
            assert b"already exists" in response.data

    def test_register_missing_fields(self, client):
        """Test registration with missing fields."""
        response = client.post("/auth/register", data={"username": "testuser"})
        assert response.status_code == 200
        assert b"required" in response.data


class TestLoginRoute:
    """Test login route."""

    def test_login_get(self, client):
        """Test GET login page."""
        response = client.get("/auth/login")
        assert response.status_code == 200
        assert b"Login" in response.data

    def test_login_post_success(self, client, app, user):
        """Test successful login."""
        with app.app_context():
            response = client.post(
                "/auth/login",
                data={"username": user.username, "password": "testpass123"},
                follow_redirects=True,
            )

            assert response.status_code == 200
            assert b"Login successful" in response.data or b"My Tasks" in response.data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        response = client.post(
            "/auth/login", data={"username": "wronguser", "password": "wrongpass"}
        )
        assert response.status_code == 200
        assert b"Invalid username or password" in response.data


class TestLogoutRoute:
    """Test logout route."""

    def test_logout_requires_login(self, client):
        """Test logout requires authentication."""
        response = client.get("/auth/logout", follow_redirects=True)
        # Should redirect to login
        assert response.status_code == 200

    def test_logout_success(self, authenticated_client, app, user):
        """Test successful logout."""
        with app.app_context():
            response = authenticated_client.get("/auth/logout", follow_redirects=True)
            assert response.status_code == 200
            assert b"logged out" in response.data
