"""
Comprehensive test suite for Flask Mini API.

This module contains unit tests for all API endpoints and functionality.
"""

import pytest
import json
import tempfile
import os
import uuid
from unittest.mock import patch, MagicMock
from flask import Flask

from flask_mini_api.main import app, db_manager, user_manager
from flask_mini_api.core import TaskManager, UserManager, DatabaseManager
from flask_mini_api.utils import validate_task_data, validate_user_data, generate_api_key
from flask_mini_api.auth import require_api_key, get_api_key_from_request


@pytest.fixture
def client():
    """Create test client."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False

    # Initialize database for testing
    with app.app_context():
        db_manager.init_database()

    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_task():
    """Sample task data for testing."""
    return {
        'title': 'Test Task',
        'description': 'This is a test task',
        'completed': False,
        'priority': 'medium'
    }


@pytest.fixture
def sample_user():
    """Sample user data for testing."""
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'api_key': 'test_api_key_123456789012345678901234567890'
    }


@pytest.fixture
def auth_headers(sample_user, client):
    """Authentication headers for testing."""
    # Create a test user in the database
    with app.app_context():
        if not user_manager.get_user_by_username(sample_user['username']):
            user_manager.create_user(sample_user)

    return {
        'X-API-Key': sample_user['api_key']
    }


class TestTaskEndpoints:
    """Test task-related endpoints."""

    def test_get_tasks_without_auth(self, client):
        """Test getting tasks without authentication."""
        response = client.get('/api/tasks')
        assert response.status_code == 401
        data = json.loads(response.data)
        assert data['error'] == 'Unauthorized'

    @patch('flask_mini_api.main.task_manager')
    def test_get_tasks_with_auth(self, mock_task_manager, client, auth_headers, sample_task):
        """Test getting tasks with authentication."""
        mock_task_manager.get_all_tasks.return_value = [sample_task]

        response = client.get('/api/tasks', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'tasks' in data
        assert 'count' in data
        assert data['count'] == 1

    @patch('flask_mini_api.main.task_manager')
    def test_get_task_by_id(self, mock_task_manager, client, auth_headers, sample_task):
        """Test getting a specific task by ID."""
        sample_task['id'] = 1
        mock_task_manager.get_task.return_value = sample_task

        response = client.get('/api/tasks/1', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'task' in data
        assert data['task']['title'] == 'Test Task'

    @patch('flask_mini_api.main.task_manager')
    def test_get_nonexistent_task(self, mock_task_manager, client, auth_headers):
        """Test getting a task that doesn't exist."""
        mock_task_manager.get_task.return_value = None

        response = client.get('/api/tasks/999', headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Not Found'

    def test_create_task_without_auth(self, client, sample_task):
        """Test creating a task without authentication."""
        response = client.post('/api/tasks',
                             data=json.dumps(sample_task),
                             content_type='application/json')
        assert response.status_code == 401

    @patch('flask_mini_api.main.task_manager')
    def test_create_task_with_auth(self, mock_task_manager, client, auth_headers, sample_task):
        """Test creating a task with authentication."""
        created_task = sample_task.copy()
        created_task['id'] = 1
        mock_task_manager.create_task.return_value = created_task

        response = client.post('/api/tasks',
                             data=json.dumps(sample_task),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Task created successfully'
        assert 'task' in data

    def test_create_task_invalid_data(self, client, auth_headers):
        """Test creating a task with invalid data."""
        invalid_data = {'title': ''}  # Empty title

        response = client.post('/api/tasks',
                             data=json.dumps(invalid_data),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Bad Request'

    @patch('flask_mini_api.main.task_manager')
    def test_update_task(self, mock_task_manager, client, auth_headers, sample_task):
        """Test updating a task."""
        updated_task = sample_task.copy()
        updated_task['id'] = 1
        updated_task['completed'] = True
        mock_task_manager.update_task.return_value = updated_task

        update_data = {'completed': True}
        response = client.put('/api/tasks/1',
                            data=json.dumps(update_data),
                            content_type='application/json',
                            headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Task updated successfully'

    @patch('flask_mini_api.main.task_manager')
    def test_delete_task(self, mock_task_manager, client, auth_headers):
        """Test deleting a task."""
        mock_task_manager.delete_task.return_value = True

        response = client.delete('/api/tasks/1', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'Task deleted successfully'


class TestUserEndpoints:
    """Test user-related endpoints."""

    def test_get_users_without_auth(self, client):
        """Test getting users without authentication."""
        response = client.get('/api/users')
        assert response.status_code == 401

    @patch('flask_mini_api.main.user_manager')
    def test_get_users_with_auth(self, mock_user_manager, client, auth_headers, sample_user):
        """Test getting users with authentication."""
        mock_user_manager.get_all_users.return_value = [sample_user]

        response = client.get('/api/users', headers=auth_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert 'count' in data

    @patch('flask_mini_api.main.user_manager')
    def test_create_user_with_auth(self, mock_user_manager, client, auth_headers, sample_user):
        """Test creating a user with authentication."""
        created_user = sample_user.copy()
        created_user['id'] = 1
        mock_user_manager.create_user.return_value = created_user

        response = client.post('/api/users',
                             data=json.dumps(sample_user),
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'

    def test_create_user_duplicate_username(self, client, auth_headers):
        """Creating a duplicate username should fail with a 400 error."""
        base = f"dup_{uuid.uuid4().hex[:8]}"
        with app.app_context():
            user_manager.create_user({
                'username': base,
                'email': f'{base}@example.com',
                'api_key': 'x' * 32
            })

        payload = {
            'username': base,
            'email': f'{base}2@example.com',
            'api_key': 'y' * 32
        }

        response = client.post(
            '/api/users',
            data=json.dumps(payload),
            content_type='application/json',
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Bad Request'
        assert 'exists' in data['message'].lower()

    def test_update_user_duplicate_username(self, client, auth_headers):
        """Updating a user to an existing username should return 400."""
        base_existing = f"user_{uuid.uuid4().hex[:8]}"
        base_target = f"user_{uuid.uuid4().hex[:8]}"

        with app.app_context():
            existing = user_manager.create_user({
                'username': base_existing,
                'email': f'{base_existing}@example.com',
                'api_key': 'a' * 32
            })
            target = user_manager.create_user({
                'username': base_target,
                'email': f'{base_target}@example.com',
                'api_key': 'b' * 32
            })

        response = client.put(
            f"/api/users/{target['id']}",
            data=json.dumps({'username': base_existing}),
            content_type='application/json',
            headers=auth_headers,
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['error'] == 'Bad Request'
        assert 'exists' in data['message'].lower()


class TestAuthEndpoints:
    """Test authentication-related endpoints."""

    def test_register_user(self, client):
        """Test user registration."""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com'
        }

        with patch('flask_mini_api.main.user_manager') as mock_user_manager:
            mock_user_manager.get_user_by_username.return_value = None
            mock_user_manager.create_user.return_value = {
                'id': 1,
                'username': 'newuser',
                'email': 'newuser@example.com',
                'api_key': 'generated_api_key'
            }

            response = client.post('/api/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'User registered successfully'
            assert 'api_key' in data

    def test_register_existing_user(self, client):
        """Test registering an existing user."""
        user_data = {
            'username': 'existinguser',
            'email': 'existing@example.com'
        }

        with patch('flask_mini_api.main.user_manager') as mock_user_manager:
            mock_user_manager.get_user_by_username.return_value = {'username': 'existinguser'}

            response = client.post('/api/auth/register',
                                 data=json.dumps(user_data),
                                 content_type='application/json')
            assert response.status_code == 400
            data = json.loads(response.data)
            assert data['error'] == 'Bad Request'

    def test_login_user(self, client):
        """Test user login."""
        login_data = {'username': 'testuser'}

        with patch('flask_mini_api.main.user_manager') as mock_user_manager:
            mock_user_manager.get_user_by_username.return_value = {
                'id': 1,
                'username': 'testuser',
                'email': 'test@example.com',
                'api_key': 'test_api_key'
            }

            response = client.post('/api/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Login successful'
            assert 'api_key' in data

    def test_login_nonexistent_user(self, client):
        """Test login with nonexistent user."""
        login_data = {'username': 'nonexistent'}

        with patch('flask_mini_api.main.user_manager') as mock_user_manager:
            mock_user_manager.get_user_by_username.return_value = None

            response = client.post('/api/auth/login',
                                 data=json.dumps(login_data),
                                 content_type='application/json')
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['error'] == 'Not Found'


class TestUtilityFunctions:
    """Test utility functions."""

    def test_validate_task_data(self, sample_task):
        """Test task data validation."""
        validated = validate_task_data(sample_task)
        assert validated['title'] == 'Test Task'
        assert validated['description'] == 'This is a test task'
        assert validated['completed'] is False
        assert validated['priority'] == 'medium'

    def test_validate_task_data_invalid_title(self):
        """Test task data validation with invalid title."""
        invalid_data = {'title': ''}

        with pytest.raises(Exception):  # Should raise BadRequest
            validate_task_data(invalid_data)

    def test_validate_user_data(self, sample_user):
        """Test user data validation."""
        validated = validate_user_data(sample_user)
        assert validated['username'] == 'testuser'
        assert validated['email'] == 'test@example.com'
        assert validated['api_key'] == 'test_api_key_123456789012345678901234567890'

    def test_validate_user_data_invalid_email(self):
        """Test user data validation with invalid email."""
        invalid_data = {
            'username': 'testuser',
            'email': 'invalid-email'
        }

        with pytest.raises(Exception):  # Should raise BadRequest
            validate_user_data(invalid_data)

    def test_generate_api_key(self):
        """Test API key generation."""
        api_key = generate_api_key()
        assert isinstance(api_key, str)
        assert len(api_key) == 32
        assert api_key.isalnum()


class TestErrorHandling:
    """Test error handling."""

    def test_404_error(self, client, auth_headers):
        """Test 404 error handling."""
        response = client.get('/api/nonexistent', headers=auth_headers)
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['error'] == 'Not Found'

    def test_400_error_invalid_json(self, client, auth_headers):
        """Test 400 error handling for invalid JSON."""
        response = client.post('/api/tasks',
                             data='invalid json',
                             content_type='application/json',
                             headers=auth_headers)
        assert response.status_code == 400

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'


class TestCoreClasses:
    """Test core business logic classes."""

    def test_task_manager_creation(self):
        """Test TaskManager initialization."""
        task_manager = TaskManager()
        assert task_manager.tasks == []
        assert task_manager.next_id == 1

    def test_user_manager_creation(self):
        """Test UserManager initialization."""
        user_manager = UserManager()
        assert user_manager.users == []
        assert user_manager.next_id == 1

    def test_database_manager_creation(self):
        """Test DatabaseManager initialization."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name

        try:
            db_manager = DatabaseManager(db_path)
            assert db_manager.db_path == db_path
        finally:
            os.unlink(db_path)


if __name__ == '__main__':
    pytest.main([__file__])
