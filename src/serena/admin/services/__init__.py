"""Admin services package"""

from typing import TYPE_CHECKING

from serena.admin.services.config_service import ConfigService
from serena.admin.services.monitoring_service import MonitoringService
from serena.admin.services.project_service import ProjectService
from serena.admin.services.tool_service import ToolService

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


def get_config_service(agent: "SerenaAgent") -> ConfigService:
    """
    Factory function to get or create a ConfigService instance.

    Args:
        agent: The SerenaAgent instance

    Returns:
        A ConfigService instance

    """
    return ConfigService(agent)


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


def get_monitoring_service(agent: "SerenaAgent") -> MonitoringService:
    """
    Factory function to get or create a MonitoringService instance.

    Args:
        agent: The SerenaAgent instance

    Returns:
        A MonitoringService instance

    """
    return MonitoringService(agent)


__all__ = [
    "ConfigService",
    "MonitoringService",
    "ProjectService",
    "ToolService",
    "get_config_service",
    "get_monitoring_service",
    "get_project_service",
    "get_tool_service",
]
