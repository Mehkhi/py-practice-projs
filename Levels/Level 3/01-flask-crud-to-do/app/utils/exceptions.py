"""Custom exception classes."""


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""

    pass


class TaskAccessDeniedError(Exception):
    """Raised when user tries to access a task they don't own."""

    pass


class UserNotFoundError(Exception):
    """Raised when a user is not found."""

    pass


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    pass


class ValidationError(Exception):
    """Raised when validation fails."""

    pass
