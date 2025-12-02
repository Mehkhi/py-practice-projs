"""
Utility functions for the Flask Mini API.

This module contains helper functions for validation, data processing, and other utilities.
"""

import re
import secrets
import string
from typing import Dict, Any, Optional
from werkzeug.exceptions import BadRequest


def validate_task_data(data: Dict[str, Any], partial: bool = False) -> Dict[str, Any]:
    """
    Validate task data.

    Args:
        data: Task data to validate
        partial: Whether this is a partial update

    Returns:
        Validated task data

    Raises:
        BadRequest: If validation fails
    """
    validated = {}

    # Title validation
    if 'title' in data:
        title = data['title']
        if not isinstance(title, str):
            raise BadRequest("Title must be a string")
        if not title.strip():
            raise BadRequest("Title cannot be empty")
        if len(title) > 200:
            raise BadRequest("Title must be 200 characters or less")
        validated['title'] = title.strip()
    elif not partial:
        raise BadRequest("Title is required")

    # Description validation
    if 'description' in data:
        description = data['description']
        if not isinstance(description, str):
            raise BadRequest("Description must be a string")
        if len(description) > 1000:
            raise BadRequest("Description must be 1000 characters or less")
        validated['description'] = description.strip()

    # Completed validation
    if 'completed' in data:
        completed = data['completed']
        if not isinstance(completed, bool):
            raise BadRequest("Completed must be a boolean")
        validated['completed'] = completed

    # Priority validation
    if 'priority' in data:
        priority = data['priority']
        if not isinstance(priority, str):
            raise BadRequest("Priority must be a string")
        if priority not in ['low', 'medium', 'high']:
            raise BadRequest("Priority must be 'low', 'medium', or 'high'")
        validated['priority'] = priority

    return validated


def validate_user_data(data: Dict[str, Any], partial: bool = False) -> Dict[str, Any]:
    """
    Validate user data.

    Args:
        data: User data to validate
        partial: Whether this is a partial update

    Returns:
        Validated user data

    Raises:
        BadRequest: If validation fails
    """
    validated = {}

    # Username validation
    if 'username' in data:
        username = data['username']
        if not isinstance(username, str):
            raise BadRequest("Username must be a string")
        if not username.strip():
            raise BadRequest("Username cannot be empty")
        if len(username) < 3:
            raise BadRequest("Username must be at least 3 characters long")
        if len(username) > 50:
            raise BadRequest("Username must be 50 characters or less")
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise BadRequest("Username can only contain letters, numbers, and underscores")
        validated['username'] = username.strip()
    elif not partial:
        raise BadRequest("Username is required")

    # Email validation
    if 'email' in data:
        email = data['email']
        if not isinstance(email, str):
            raise BadRequest("Email must be a string")
        if not email.strip():
            raise BadRequest("Email cannot be empty")
        if len(email) > 100:
            raise BadRequest("Email must be 100 characters or less")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise BadRequest("Invalid email format")
        validated['email'] = email.strip().lower()
    elif not partial:
        raise BadRequest("Email is required")

    # API key validation
    if 'api_key' in data:
        api_key = data['api_key']
        if not isinstance(api_key, str):
            raise BadRequest("API key must be a string")
        if not api_key.strip():
            raise BadRequest("API key cannot be empty")
        if len(api_key) < 32:
            raise BadRequest("API key must be at least 32 characters long")
        validated['api_key'] = api_key.strip()

    return validated


def generate_api_key(length: int = 32) -> str:
    """
    Generate a secure API key.

    Args:
        length: Length of the API key

    Returns:
        Generated API key
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input.

    Args:
        text: Text to sanitize
        max_length: Maximum length of the text

    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', text)

    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized.strip()


def format_error_message(error: Exception) -> str:
    """
    Format error message for API response.

    Args:
        error: Exception to format

    Returns:
        Formatted error message
    """
    error_type = type(error).__name__
    error_message = str(error)

    # Remove sensitive information
    if 'password' in error_message.lower():
        error_message = "Authentication error"
    elif 'key' in error_message.lower() and 'api' in error_message.lower():
        error_message = "API key error"

    return f"{error_type}: {error_message}"


def validate_pagination_params(page: int, per_page: int) -> tuple:
    """
    Validate pagination parameters.

    Args:
        page: Page number
        per_page: Items per page

    Returns:
        Validated page and per_page values

    Raises:
        BadRequest: If validation fails
    """
    if page < 1:
        raise BadRequest("Page must be 1 or greater")

    if per_page < 1:
        raise BadRequest("Per page must be 1 or greater")

    if per_page > 100:
        raise BadRequest("Per page cannot exceed 100")

    return page, per_page


def calculate_pagination_offset(page: int, per_page: int) -> int:
    """
    Calculate pagination offset.

    Args:
        page: Page number
        per_page: Items per page

    Returns:
        Offset value
    """
    return (page - 1) * per_page


def format_response_data(data: Any, message: str = None) -> Dict[str, Any]:
    """
    Format response data for API.

    Args:
        data: Data to format
        message: Optional message

    Returns:
        Formatted response data
    """
    response = {
        'success': True,
        'data': data
    }

    if message:
        response['message'] = message

    return response


def format_error_response(error: str, status_code: int = 400) -> Dict[str, Any]:
    """
    Format error response for API.

    Args:
        error: Error message
        status_code: HTTP status code

    Returns:
        Formatted error response
    """
    return {
        'success': False,
        'error': error,
        'status_code': status_code
    }
