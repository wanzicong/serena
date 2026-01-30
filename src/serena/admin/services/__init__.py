"""Admin services package"""

from typing import TYPE_CHECKING

from serena.admin.services.project_service import ProjectService

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


def get_project_service(agent: "SerenaAgent") -> ProjectService:
    """
    Factory function to get or create a ProjectService instance.

    Args:
        agent: The SerenaAgent instance

    Returns:
        A ProjectService instance

    """
    return ProjectService(agent)


__all__ = ["ProjectService", "get_project_service"]
