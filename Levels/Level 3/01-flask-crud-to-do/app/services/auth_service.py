"""Authentication service for user management."""

import logging
from typing import Optional

from sqlalchemy.exc import IntegrityError

from app import db
from app.models.user import User
from app.utils.exceptions import ValidationError

logger = logging.getLogger(__name__)


def register_user(username: str, email: str, password: str) -> User:
    """Register a new user.

    Args:
        username: Unique username
        email: Unique email address
        password: Plain text password

    Returns:
        Created User instance

    Raises:
        ValidationError: If username or email already exists
    """
    logger.info(f"Attempting to register user: {username}")

    # Check if user already exists
    if User.query.filter_by(username=username).first():
        logger.warning(f"Registration failed: username {username} already exists")
        raise ValidationError(f"Username {username} already exists")

    if User.query.filter_by(email=email).first():
        logger.warning(f"Registration failed: email {email} already exists")
        raise ValidationError(f"Email {email} already exists")

    # Create new user
    user = User(username=username, email=email)
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        logger.info(f"User {username} registered successfully")
        return user
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database error during registration: {e}")
        raise ValidationError("Registration failed due to database error") from e


def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user with username and password.

    Args:
        username: Username
        password: Plain text password

    Returns:
        User instance if authentication successful, None otherwise
    """
    logger.info(f"Attempting to authenticate user: {username}")

    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        logger.info(f"User {username} authenticated successfully")
        return user

    logger.warning(f"Authentication failed for user: {username}")
    return None
