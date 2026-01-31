"""测试 ToolExecutorService"""

import pytest
from unittest.mock import MagicMock, Mock


@pytest.fixture(autouse=True)
def reset_singleton():
    """在每个测试前重置单例"""
    import sys
    if "serena.admin.services.tool_executor_service" in sys.modules:
        module = sys.modules["serena.admin.services.tool_executor_service"]
        module._tool_executor_service = None
    yield


def test_get_all_tools_returns_list():
    """测试获取所有工具列表"""
    mock_agent = MagicMock()
    mock_tool1 = Mock()
    mock_tool1.get_name.return_value = "read_file"
    mock_tool1.__name__ = "read_file"
    mock_tool1.__doc__ = "Read a file from the filesystem."

    mock_tool2 = Mock()
    mock_tool2.get_name.return_value = "find_symbol"
    mock_tool2.__name__ = "find_symbol"
    mock_tool2.__doc__ = "Find symbols in codebase."

    mock_agent.get_exposed_tool_instances.return_value = [mock_tool1, mock_tool2]

    from serena.admin.services.tool_executor_service import get_tool_executor_service
    service = get_tool_executor_service(mock_agent)
    tools = service.get_all_tools()

    assert len(tools) == 2
    assert tools[0]["name"] == "read_file"
    assert tools[1]["name"] == "find_symbol"


def test_get_tool_schema():
    """测试获取工具的参数 schema"""
    mock_agent = MagicMock()
    mock_tool = MagicMock()
    mock_tool.get_name.return_value = "read_file"

    # 模拟 _all_tools 为包含工具的字典
    mock_agent._all_tools = {"read_file": mock_tool}

    from serena.admin.services.tool_executor_service import get_tool_executor_service
    service = get_tool_executor_service(mock_agent)
    schema = service.get_tool_schema("read_file")

    assert "parameters" in schema
    assert schema["name"] == "read_file"
