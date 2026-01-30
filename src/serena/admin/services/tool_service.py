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

    def get_tool_statistics(self) -> dict[str, Any]:
        """
        Get detailed tool usage statistics.

        Returns:
            A dictionary containing:
            - total_tools: Total number of tools
            - active_tools: Number of active tools
            - total_calls: Total number of tool calls
            - total_input_tokens: Total input tokens across all tools
            - total_output_tokens: Total output tokens across all tools
            - tools: List of tool statistics with details
            - most_used_tools: Top 5 most used tools
            - token_estimator_name: Name of the token estimator being used

        """
        tools = self.get_all_tools()
        active_tools = [t for t in tools if t["is_active"]]
        total_calls = sum(t["calls"] for t in tools)

        # Get detailed stats from analytics
        tool_stats_dict = {}
        total_input_tokens = 0
        total_output_tokens = 0

        if self._agent._tool_usage_stats:
            tool_stats_dict = self._agent._tool_usage_stats.get_tool_stats_dict()
            for stats in tool_stats_dict.values():
                total_input_tokens += stats.get("input_tokens", 0)
                total_output_tokens += stats.get("output_tokens", 0)

        # Merge call counts with detailed stats
        detailed_tools = []
        for tool in tools:
            tool_name = tool["name"]
            detailed_stats = tool_stats_dict.get(tool_name, {})
            detailed_tools.append(
                {
                    "name": tool_name,
                    "is_active": tool["is_active"],
                    "calls": tool["calls"],
                    "input_tokens": detailed_stats.get("input_tokens", 0),
                    "output_tokens": detailed_stats.get("output_tokens", 0),
                    "total_tokens": detailed_stats.get("input_tokens", 0) + detailed_stats.get("output_tokens", 0),
                    "avg_input_tokens": (detailed_stats.get("input_tokens", 0) // tool["calls"] if tool["calls"] > 0 else 0),
                    "avg_output_tokens": (detailed_stats.get("output_tokens", 0) // tool["calls"] if tool["calls"] > 0 else 0),
                }
            )

        # Sort by call count and get top 5
        most_used_tools = sorted(detailed_tools, key=lambda x: x["calls"], reverse=True)[:5]

        # Sort tools by name for consistent display
        detailed_tools.sort(key=lambda x: x["name"])

        return {
            "total_tools": len(tools),
            "active_tools": len(active_tools),
            "total_calls": total_calls,
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_input_tokens + total_output_tokens,
            "token_estimator_name": (self._agent._tool_usage_stats.token_estimator_name if self._agent._tool_usage_stats else "未配置"),
            "tools": detailed_tools,
            "most_used_tools": most_used_tools,
        }
