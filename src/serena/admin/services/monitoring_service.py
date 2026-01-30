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

    def get_lsp_detailed_status(self) -> dict[str, Any]:
        """
        Get detailed status information about all active LSP servers.

        Returns:
            A dictionary containing:
            - total_servers: Total number of LSP servers
            - servers: List of detailed server information including:
                - language: Programming language
                - language_server: Language server name
                - status: Running status
                - project_path: Project root path
            - supported_languages: List of all supported languages

        """
        from solidlsp.ls_config import Language

        ls_manager = self._agent.get_language_server_manager()
        servers = []

        if ls_manager:
            active_languages = ls_manager.get_active_languages()
            project_path = ls_manager.get_root_path()

            for lang in active_languages:
                servers.append(
                    {
                        "language": lang.value,
                        "language_server": f"{lang.value}-language-server",
                        "status": "运行中",
                        "project_path": project_path,
                    }
                )

        # Get all supported languages
        supported_languages = [lang.value for lang in Language]

        return {
            "total_servers": len(servers),
            "servers": servers,
            "supported_languages": sorted(supported_languages),
        }

    def get_logs(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent log entries.

        Args:
            limit: Maximum number of log entries to return

        Returns:
            A list of dictionaries containing log information including:
            - timestamp: Log timestamp
            - level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            - logger: Logger name
            - message: Log message

        """
        import os

        logs = []

        # Try to get logs from a log file if it exists
        log_file = self._get_log_file()
        if log_file and os.path.exists(log_file):
            try:
                with open(log_file, encoding="utf-8") as f:
                    lines = f.readlines()
                    # Get the last 'limit' lines
                    for line in lines[-limit:]:
                        log_entry = self._parse_log_line(line)
                        if log_entry:
                            logs.append(log_entry)
            except Exception:
                pass

        # If no logs from file, return some default system logs
        if not logs:
            logs = self._get_system_logs(limit)

        return logs

    def _get_log_file(self) -> str | None:
        """Get the path to the log file if configured."""
        import os

        # Check common log file locations
        possible_paths = [
            "serena.log",
            "logs/serena.log",
            ".serena/logs/serena.log",
            os.path.expanduser("~/.serena/logs/serena.log"),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        return None

    def _parse_log_line(self, line: str) -> dict[str, Any] | None:
        """
        Parse a log line into structured data.

        Args:
            line: Raw log line

        Returns:
            Dictionary with parsed log data or None if parsing fails

        """
        import re

        # Try to match standard Python log format
        # Example: 2024-01-01 12:00:00,123 - INFO - serena.agent - Message
        pattern = r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}[,\.]\d+)\s*-\s*(\w+)\s*-\s*(\S+)\s*-\s*(.+)"
        match = re.match(pattern, line.strip())

        if match:
            return {"timestamp": match.group(1), "level": match.group(2), "logger": match.group(3), "message": match.group(4)}

        # If line doesn't match standard format, return as-is with INFO level
        if line.strip():
            return {"timestamp": "", "level": "INFO", "logger": "system", "message": line.strip()}

        return None

    def _get_system_logs(self, limit: int) -> list[dict[str, Any]]:
        """
        Get system-generated logs as fallback.

        Args:
            limit: Maximum number of log entries

        Returns:
            List of log entry dictionaries

        """
        from datetime import datetime

        logs = []

        # Add some system status logs
        active_project = self._agent.get_active_project()
        lsp_languages = self._agent.get_active_lsp_languages()
        current_tasks = self._agent.get_current_tasks()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logs.append(
            {
                "timestamp": timestamp,
                "level": "INFO",
                "logger": "system",
                "message": f"活跃项目: {active_project.project_name if active_project else '无'}",
            }
        )

        logs.append({"timestamp": timestamp, "level": "INFO", "logger": "system", "message": f"LSP 服务器数量: {len(lsp_languages)}"})

        logs.append({"timestamp": timestamp, "level": "INFO", "logger": "system", "message": f"活跃任务数量: {len(current_tasks)}"})

        if lsp_languages:
            for lang in lsp_languages:
                logs.append({"timestamp": timestamp, "level": "INFO", "logger": "lsp", "message": f"LSP 语言服务器运行中: {lang.value}"})

        if current_tasks:
            for task in current_tasks:
                logs.append(
                    {
                        "timestamp": timestamp,
                        "level": "INFO",
                        "logger": "tasks",
                        "message": f"任务: {task.name} - {'运行中' if task.is_running else '已完成'}",
                    }
                )

        return logs[:limit]
