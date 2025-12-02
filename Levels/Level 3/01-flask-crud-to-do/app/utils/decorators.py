"""Custom decorators."""

from functools import wraps
from typing import Callable, TypeVar, cast

from flask import abort
from flask_login import current_user

F = TypeVar("F", bound=Callable)


def login_required(f: F) -> F:
    """Decorator to require user login.

    Args:
        f: Function to decorate

    Returns:
        Decorated function that checks authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):  # type: ignore
        if not current_user.is_authenticated:
            abort(401)
        return f(*args, **kwargs)

    return cast(F, decorated_function)
