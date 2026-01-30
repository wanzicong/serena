"""Tool management business logic"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


class ToolService:
    """
    Service class for managing tools in the admin dashboard.
    """

    def __init__(self, agent: "SerenaAgent") -> None:
        """
        Initialize the ToolService.

        Args:
            agent: The SerenaAgent instance

        """
        self._agent = agent

    def get_all_tools(self) -> list[dict[str, Any]]:
        """
        Get all tools with their status and statistics.

        Returns:
            A list of dictionaries containing tool information including:
            - name: Tool name
            - is_active: Whether the tool is currently active
            - calls: Number of times the tool has been called

        """
        tools = []
        active_tools = self._agent.get_active_tool_names()
        all_tool_names = sorted([tool.get_name_from_cls() for tool in self._agent._all_tools.values()])

        for tool_name in all_tool_names:
            tools.append(
                {
                    "name": tool_name,
                    "is_active": tool_name in active_tools,
                    "calls": self._get_tool_call_count(tool_name),
                }
            )

        return tools

    def _get_tool_call_count(self, tool_name: str) -> int:
        """
        Get tool call count from stats.

        Args:
            tool_name: The name of the tool

        Returns:
            The number of times the tool has been called

        """
        if self._agent._tool_usage_stats:
            stats = self._agent._tool_usage_stats.get_tool_stats_dict()
            return stats.get(tool_name, {}).get("num_times_called", 0)
        return 0

    def toggle_tool(self, tool_name: str, enabled: bool) -> None:
        """
        Toggle tool enabled/disabled.

        Args:
            tool_name: The name of the tool to toggle
            enabled: Whether the tool should be enabled

        Raises:
            NotImplementedError: This feature is not yet implemented

        """
        # TODO: Implementation will modify project config
        raise NotImplementedError("工具切换功能尚未实现")
