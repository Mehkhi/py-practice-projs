"""Flask application factory."""

import logging
import os
from typing import Optional

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy(session_options={"expire_on_commit": False})
login_manager = LoginManager()
migrate = Migrate()


def create_app(config_name: Optional[str] = None) -> Flask:
    """Create and configure Flask application.

    Args:
        config_name: Configuration name (development, testing, production).
                     If None, uses FLASK_ENV environment variable.

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///todo_app.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_EXPIRE_ON_COMMIT"] = False

    # Determine environment
    env = config_name or os.environ.get("FLASK_ENV", "development")
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "0") == "1"

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    migrate.init_app(app, db)

    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id: str) -> Optional["User"]:  # type: ignore
        """Load user by ID for Flask-Login.

        Args:
            user_id: User ID as string

        Returns:
            User instance or None
        """
        from app.models.user import User

        return User.query.get(int(user_id))

    # Setup logging
    logging.basicConfig(
        level=logging.INFO if not app.debug else logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info(f"Application initialized in {env} mode")

    # Import models to register them with SQLAlchemy
    from app.models import (  # noqa: F401
        AuditLog,
        Task,
        TaskAttachment,
        TaskDependency,
        TaskNote,
        TaskTemplate,
        TimeEntry,
        User,
    )

    # Register blueprints
    from app.routes import auth_bp, tasks_bp, main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")

    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created/verified")

    return app
