"""System monitoring business logic"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


class MonitoringService:
    """
    Service class for system monitoring in the admin dashboard.
    """

    def __init__(self, agent: "SerenaAgent") -> None:
        """
        Initialize the MonitoringService.

        Args:
            agent: The SerenaAgent instance

        """
        self._agent = agent

    def get_system_status(self) -> dict[str, Any]:
        """
        Get overall system status.

        Returns:
            A dictionary containing:
            - lsp_servers: Number of active LSP servers
            - active_tasks: Number of currently active tasks
            - active_project: Name of the active project or None
            - lsp_languages: List of active LSP languages

        """
        lsp_languages = self._agent.get_active_lsp_languages()
        current_tasks = self._agent.get_current_tasks()
        active_project = self._agent.get_active_project()

        return {
            "lsp_servers": len(lsp_languages),
            "active_tasks": len(current_tasks),
            "active_project": active_project.project_name if active_project else None,
            "lsp_languages": [lang.value for lang in lsp_languages],
        }

    def get_tasks_info(self) -> list[dict[str, Any]]:
        """
        Get information about current tasks.

        Returns:
            A list of dictionaries containing task information including:
            - name: Task name
            - status: Task status (running, queued, completed)
            - logged: Whether the task is logged

        """
        current_tasks = self._agent.get_current_tasks()

        tasks_info = []
        for task in current_tasks:
            # Determine status based on is_running flag
            if task.is_running:
                status = "running"
            elif not task.future.done():
                status = "queued"
            else:
                status = "completed"

            tasks_info.append(
                {
                    "name": task.name,
                    "status": status,
                    "logged": task.logged,
                }
            )

        return tasks_info

    def get_lsp_info(self) -> list[dict[str, Any]]:
        """
        Get information about active LSP servers.

        Returns:
            A list of dictionaries containing LSP information including:
            - language: Programming language
            - language_server: Language server name

        """
        lsp_languages = self._agent.get_active_lsp_languages()

        lsp_info = []
        for lang in lsp_languages:
            lsp_info.append(
                {
                    "language": lang.value,
                    "language_server": f"{lang.value}-language-server",
                }
            )

        return lsp_info
