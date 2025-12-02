"""
Authentication module for the Flask Mini API.

This module handles API key authentication and authorization.
"""

import logging
from functools import wraps
from typing import Optional
from flask import request, jsonify
from werkzeug.exceptions import Unauthorized

from .core import UserManager

logger = logging.getLogger(__name__)

# Initialize user manager for authentication
user_manager = UserManager()


def require_api_key(f):
    """
    Decorator to require API key authentication.

    Args:
        f: Function to decorate

    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = get_api_key_from_request()

        if not api_key:
            logger.warning("API request without API key")
            return jsonify({
                'error': 'Unauthorized',
                'message': 'API key is required',
                'status_code': 401
            }), 401

        user = user_manager.get_user_by_api_key(api_key)
        if not user:
            logger.warning(f"Invalid API key: {api_key[:8]}...")
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid API key',
                'status_code': 401
            }), 401

        # Add user to request context for use in route handlers
        request.current_user = user
        logger.info(f"Authenticated user: {user['username']}")

        return f(*args, **kwargs)

    return decorated_function


def get_api_key_from_request() -> Optional[str]:
    """
    Extract API key from request.

    Returns:
        API key if found, None otherwise
    """
    # Check Authorization header
    auth_header = request.headers.get('Authorization')
    if auth_header:
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        elif auth_header.startswith('ApiKey '):
            return auth_header[7:]  # Remove 'ApiKey ' prefix
        else:
            return auth_header

    # Check X-API-Key header
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return api_key

    # Check query parameter
    api_key = request.args.get('api_key')
    if api_key:
        return api_key

    return None


def validate_api_key(api_key: str) -> bool:
    """
    Validate API key format and existence.

    Args:
        api_key: API key to validate

    Returns:
        True if valid, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False

    if len(api_key) < 32:
        return False

    # Check if API key exists in database
    user = user_manager.get_user_by_api_key(api_key)
    return user is not None


def get_current_user():
    """
    Get current authenticated user from request context.

    Returns:
        Current user or None
    """
    return getattr(request, 'current_user', None)


def require_admin(f):
    """
    Decorator to require admin privileges.

    Args:
        f: Function to decorate

    Returns:
        Decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()

        if not user:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authentication required',
                'status_code': 401
            }), 401

        # Check if user is admin (for future use)
        # For now, all authenticated users are considered admins
        if not user.get('is_admin', True):
            return jsonify({
                'error': 'Forbidden',
                'message': 'Admin privileges required',
                'status_code': 403
            }), 403

        return f(*args, **kwargs)

    return decorated_function


def log_authentication_attempt(api_key: str, success: bool, user_agent: str = None):
    """
    Log authentication attempt.

    Args:
        api_key: API key used
        success: Whether authentication was successful
        user_agent: User agent string
    """
    masked_key = f"{api_key[:8]}..." if api_key else "None"
    status = "SUCCESS" if success else "FAILED"

    log_message = f"Authentication attempt - Key: {masked_key}, Status: {status}"
    if user_agent:
        log_message += f", User-Agent: {user_agent}"

    if success:
        logger.info(log_message)
    else:
        logger.warning(log_message)
