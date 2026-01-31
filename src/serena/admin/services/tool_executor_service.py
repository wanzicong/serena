"""Tool executor service for admin dashboard."""

import time
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


class ToolExecutorService:
    """Service for executing Serena tools through web interface."""

    def __init__(self, agent: "SerenaAgent") -> None:
        """Initialize the tool executor service.

        Args:
            agent: The SerenaAgent instance
        """
        self._agent = agent

    def get_all_tools(self) -> list[dict[str, Any]]:
        """Get all exposed tools with their metadata.

        Returns:
            A list of tool dictionaries containing name, description, and category
        """
        tools = []
        for tool in self._agent.get_exposed_tool_instances():
            tools.append({
                "name": tool.get_name(),
                "description": getattr(tool, "__doc__", "").split("\n")[0] if tool.__doc__ else "",
            })
        return tools

    def get_tool_schema(self, tool_name: str) -> dict[str, Any]:
        """Get the parameter schema for a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            A dictionary containing tool metadata and parameter schema
        """
        # Find the tool by name
        for tool in self._agent._all_tools.values():
            if tool.get_name() == tool_name:
                return {
                    "name": tool_name,
                    "parameters": self._extract_parameters(tool),
                }
        raise ValueError(f"Tool '{tool_name}' not found")

    def execute_tool(self, tool_name: str, params: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool with the given parameters.

        Args:
            tool_name: Name of the tool to execute
            params: Parameters to pass to the tool

        Returns:
            A dictionary containing execution result and metadata

        Raises:
            ValueError: If tool is not found
        """
        start_time = time.time()

        # Find the tool
        tool = None
        for t in self._agent._all_tools.values():
            if t.get_name() == tool_name:
                tool = t
                break

        if tool is None:
            raise ValueError(f"Tool '{tool_name}' not found")

        try:
            # Execute the tool
            result = tool.run(**params)
            elapsed = time.time() - start_time

            return {
                "status": "success",
                "content": result,
                "metadata": {
                    "tool_name": tool_name,
                    "elapsed_ms": round(elapsed * 1000, 2),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }
        except Exception as e:
            elapsed = time.time() - start_time
            return {
                "status": "error",
                "error": str(e),
                "metadata": {
                    "tool_name": tool_name,
                    "elapsed_ms": round(elapsed * 1000, 2),
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                },
            }

    def _extract_parameters(self, tool: Any) -> dict[str, Any]:
        """Extract parameter schema from tool."""
        # Placeholder - will be implemented in next task
        return {}


# Singleton instance
_tool_executor_service: ToolExecutorService | None = None


def get_tool_executor_service(agent: "SerenaAgent") -> ToolExecutorService:
    """Get or create the ToolExecutorService singleton.

    Args:
        agent: The SerenaAgent instance

    Returns:
        The ToolExecutorService instance
    """
    global _tool_executor_service
    if _tool_executor_service is None:
        _tool_executor_service = ToolExecutorService(agent)
    return _tool_executor_service
