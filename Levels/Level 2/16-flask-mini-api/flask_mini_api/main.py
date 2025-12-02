"""
Main Flask application entry point.

This module contains the Flask app configuration and route definitions.
"""

import logging
from typing import Dict, Any, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

from .core import TaskManager, UserManager, DatabaseManager
from .utils import validate_task_data, validate_user_data, generate_api_key
from .auth import require_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize managers
db_manager = DatabaseManager()
task_manager = TaskManager(db_manager=db_manager)
user_manager = UserManager(db_manager=db_manager)

# Configure app
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['JSON_SORT_KEYS'] = False


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 Bad Request errors."""
    logger.warning(f"Bad request: {error}")
    return jsonify({
        'error': 'Bad Request',
        'message': str(error),
        'status_code': 400
    }), 400


@app.errorhandler(404)
def not_found(error):
    """Handle 404 Not Found errors."""
    logger.warning(f"Not found: {error}")
    return jsonify({
        'error': 'Not Found',
        'message': 'Resource not found',
        'status_code': 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 Internal Server errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal Server Error',
        'message': 'An unexpected error occurred',
        'status_code': 500
    }), 500


# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'message': 'Flask Mini API is running',
        'version': '1.0.0'
    })


# Task endpoints
@app.route('/api/tasks', methods=['GET'])
@require_api_key
def get_tasks():
    """Get all tasks."""
    try:
        tasks = task_manager.get_all_tasks()
        logger.info(f"Retrieved {len(tasks)} tasks")
        return jsonify({
            'tasks': tasks,
            'count': len(tasks)
        })
    except Exception as e:
        logger.error(f"Error retrieving tasks: {e}")
        raise InternalServerError("Failed to retrieve tasks")


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
@require_api_key
def get_task(task_id: int):
    """Get a specific task by ID."""
    try:
        task = task_manager.get_task(task_id)
        if not task:
            raise NotFound(f"Task with ID {task_id} not found")

        logger.info(f"Retrieved task {task_id}")
        return jsonify({'task': task})
    except NotFound:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {e}")
        raise InternalServerError("Failed to retrieve task")


@app.route('/api/tasks', methods=['POST'])
@require_api_key
def create_task():
    """Create a new task."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Request body must be JSON")

        # Validate task data
        validated_data = validate_task_data(data)

        task = task_manager.create_task(validated_data)
        logger.info(f"Created task {task['id']}: {task['title']}")

        return jsonify({
            'message': 'Task created successfully',
            'task': task
        }), 201
    except BadRequest as e:
        raise
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise InternalServerError("Failed to create task")


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
@require_api_key
def update_task(task_id: int):
    """Update an existing task."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Request body must be JSON")

        # Validate task data
        validated_data = validate_task_data(data, partial=True)

        task = task_manager.update_task(task_id, validated_data)
        if not task:
            raise NotFound(f"Task with ID {task_id} not found")

        logger.info(f"Updated task {task_id}")
        return jsonify({
            'message': 'Task updated successfully',
            'task': task
        })
    except (BadRequest, NotFound) as e:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise InternalServerError("Failed to update task")


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@require_api_key
def delete_task(task_id: int):
    """Delete a task."""
    try:
        success = task_manager.delete_task(task_id)
        if not success:
            raise NotFound(f"Task with ID {task_id} not found")

        logger.info(f"Deleted task {task_id}")
        return jsonify({
            'message': 'Task deleted successfully'
        })
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise InternalServerError("Failed to delete task")


# User endpoints
@app.route('/api/users', methods=['GET'])
@require_api_key
def get_users():
    """Get all users."""
    try:
        users = user_manager.get_all_users()
        logger.info(f"Retrieved {len(users)} users")
        return jsonify({
            'users': users,
            'count': len(users)
        })
    except Exception as e:
        logger.error(f"Error retrieving users: {e}")
        raise InternalServerError("Failed to retrieve users")


@app.route('/api/users/<int:user_id>', methods=['GET'])
@require_api_key
def get_user(user_id: int):
    """Get a specific user by ID."""
    try:
        user = user_manager.get_user(user_id)
        if not user:
            raise NotFound(f"User with ID {user_id} not found")

        logger.info(f"Retrieved user {user_id}")
        return jsonify({'user': user})
    except NotFound:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user {user_id}: {e}")
        raise InternalServerError("Failed to retrieve user")


@app.route('/api/users', methods=['POST'])
@require_api_key
def create_user():
    """Create a new user."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Request body must be JSON")

        # Validate user data
        validated_data = validate_user_data(data)

        user = user_manager.create_user(validated_data)
        logger.info(f"Created user {user['id']}: {user['username']}")

        return jsonify({
            'message': 'User created successfully',
            'user': user
        }), 201
    except BadRequest as e:
        raise
    except ValueError as e:
        raise BadRequest(str(e))
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise InternalServerError("Failed to create user")


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@require_api_key
def update_user(user_id: int):
    """Update an existing user."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Request body must be JSON")

        # Validate user data
        validated_data = validate_user_data(data, partial=True)

        user = user_manager.update_user(user_id, validated_data)
        if not user:
            raise NotFound(f"User with ID {user_id} not found")

        logger.info(f"Updated user {user_id}")
        return jsonify({
            'message': 'User updated successfully',
            'user': user
        })
    except (BadRequest, NotFound) as e:
        raise
    except ValueError as e:
        raise BadRequest(str(e))
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}")
        raise InternalServerError("Failed to update user")


@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_api_key
def delete_user(user_id: int):
    """Delete a user."""
    try:
        success = user_manager.delete_user(user_id)
        if not success:
            raise NotFound(f"User with ID {user_id} not found")

        logger.info(f"Deleted user {user_id}")
        return jsonify({
            'message': 'User deleted successfully'
        })
    except NotFound as e:
        raise
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}")
        raise InternalServerError("Failed to delete user")


# API key management endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user and get API key."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Request body must be JSON")

        username = data.get('username')
        email = data.get('email')

        if not username or not email:
            raise BadRequest("Username and email are required")

        # Check if user already exists
        existing_user = user_manager.get_user_by_username(username)
        if existing_user:
            raise BadRequest("Username already exists")

        # Create user
        user_data = {
            'username': username,
            'email': email,
            'api_key': generate_api_key()
        }

        user = user_manager.create_user(user_data)
        logger.info(f"Registered new user: {username}")

        return jsonify({
            'message': 'User registered successfully',
            'user': user,
            'api_key': user['api_key']
        }), 201
    except BadRequest as e:
        raise
    except ValueError as e:
        raise BadRequest(str(e))
    except Exception as e:
        logger.error(f"Error registering user: {e}")
        raise InternalServerError("Failed to register user")


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login with username and get API key."""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Request body must be JSON")

        username = data.get('username')
        if not username:
            raise BadRequest("Username is required")

        user = user_manager.get_user_by_username(username)
        if not user:
            raise NotFound("User not found")

        logger.info(f"User {username} logged in")
        return jsonify({
            'message': 'Login successful',
            'user': user,
            'api_key': user['api_key']
        })
    except (BadRequest, NotFound) as e:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise InternalServerError("Failed to login")


if __name__ == '__main__':
    # Initialize database
    db_manager.init_database()

    # Run the Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
