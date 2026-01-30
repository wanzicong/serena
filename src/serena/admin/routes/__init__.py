"""Admin route definitions"""

from typing import TYPE_CHECKING

from flask import Blueprint, Flask

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


def register_admin_routes(app: Flask, agent: "SerenaAgent") -> None:
    """
    Register admin routes with the Flask application.

    Args:
        app: The Flask application instance
        agent: The SerenaAgent instance

    """
    # Create a blueprint for admin routes
    admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

    # Register the blueprint with the app
    # Note: No routes defined yet, this will return 404 for /admin/ paths
    app.register_blueprint(admin_bp)
