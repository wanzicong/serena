"""Tool executor service for admin dashboard."""

import inspect
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
            # Convert parameters to correct types (form sends everything as strings)
            converted_params = self._convert_params(tool, params)

            # Execute the tool (Serena tools use 'apply' method)
            result = tool.apply(**converted_params)
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

    def _convert_params(self, tool: Any, params: dict[str, Any]) -> dict[str, Any]:
        """Convert parameter values to correct types based on tool schema.

        Args:
            tool: The tool instance
            params: Raw parameters from form

        Returns:
            Converted parameters

        """
        # Get the tool's parameter schema
        param_schemas = self._extract_parameters(tool)

        converted = {}
        for param_name, param_value in params.items():
            if param_name not in param_schemas:
                converted[param_name] = param_value
                continue

            param_type = param_schemas[param_name].get("type", "string")

            # Convert based on type
            if param_value == "" or param_value is None:
                # Use default value if available
                converted[param_name] = param_schemas[param_name].get("default")
                continue

            # Handle bool type (from checkbox)
            if "bool" in param_type.lower():
                converted[param_name] = param_value in ("true", "True", "1", True)
            # Handle int type
            elif "int" in param_type.lower():
                try:
                    converted[param_name] = int(param_value)
                except (ValueError, TypeError):
                    converted[param_name] = param_value
            # Handle float type
            elif "float" in param_type.lower():
                try:
                    converted[param_name] = float(param_value)
                except (ValueError, TypeError):
                    converted[param_name] = param_value
            else:
                converted[param_name] = param_value

        return converted

    def _extract_parameters(self, tool: Any) -> dict[str, Any]:
        """Extract parameter schema from tool.

        Args:
            tool: The tool instance

        Returns:
            A dictionary mapping parameter names to their schema

        """
        try:
            # Get the apply method's signature (Serena tools use 'apply' method)
            sig = inspect.signature(tool.apply)
            parameters = {}

            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue

                param_schema = {
                    "type": str(param.annotation) if param.annotation != inspect.Parameter.empty else "string",
                    "required": param.default == inspect.Parameter.empty,
                    "default": param.default if param.default != inspect.Parameter.empty else None,
                }

                # Add description if available
                if hasattr(tool, "__doc__") and tool.__doc__:
                    # Try to extract parameter descriptions from docstring
                    param_schema["description"] = f"Parameter: {param_name}"

                parameters[param_name] = param_schema

            return parameters
        except Exception:
            # Fallback: return empty schema
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
