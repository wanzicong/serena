"""Admin services package"""

from typing import TYPE_CHECKING

from serena.admin.services.project_service import ProjectService
from serena.admin.services.tool_service import ToolService

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


def get_tool_service(agent: "SerenaAgent") -> ToolService:
    """
    Factory function to get or create a ToolService instance.

    Args:
        agent: The SerenaAgent instance

    Returns:
        A ToolService instance

    """
    return ToolService(agent)


__all__ = ["ProjectService", "ToolService", "get_project_service", "get_tool_service"]
