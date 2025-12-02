"""Route blueprints."""

from app.routes.main import main_bp
from app.routes.auth import auth_bp
from app.routes.tasks import tasks_bp

__all__ = ["main_bp", "auth_bp", "tasks_bp"]
