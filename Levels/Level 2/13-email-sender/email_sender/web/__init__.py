"""
Web Package - Flask application factory and blueprint registration.

This package provides the web interface for the email sender application.
"""

import os
import logging
from flask import Flask

from ..storage import CampaignStorage

from .campaigns import campaigns_bp, init_storage as init_campaigns_storage
from .signatures import signatures_bp, init_storage as init_signatures_storage
from .attachments import attachments_bp, init_storage as init_attachments_storage
from .tracking import tracking_bp, init_storage as init_tracking_storage

logger = logging.getLogger(__name__)


def create_app(config=None):
    """
    Application factory for creating Flask app instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Configured Flask application
    """
    # Configure Flask app with templates folder
    template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    app = Flask(__name__, template_folder=template_dir)

    # Default configuration
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Apply custom configuration if provided
    if config:
        app.config.update(config)

    # Initialize storage
    storage = CampaignStorage()

    # Initialize storage for all blueprints
    init_campaigns_storage(storage)
    init_signatures_storage(storage)
    init_attachments_storage(storage)
    init_tracking_storage(storage)

    # Register blueprints
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(signatures_bp)
    app.register_blueprint(attachments_bp)
    app.register_blueprint(tracking_bp)

    # Add security headers
    @app.after_request
    def set_response_headers(response):
        """Add security and caching headers to responses."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        return response

    logger.info("Flask app created with all blueprints registered")
    return app


def run_web_server(host: str = "127.0.0.1", port: int = 9002, debug: bool = True):
    """
    Run the web server.

    Note: Default port is 9002 to avoid conflicts with common services
    (macOS AirPlay uses 5000, many dev servers use 8000/8080).
    """
    app = create_app()
    print(f"Starting web server at http://{host}:{port}")
    if debug:
        print("Debug mode enabled - server will auto-reload on code changes")
    app.run(host=host, port=port, debug=debug)


# For backwards compatibility, create a default app instance
app = create_app()
