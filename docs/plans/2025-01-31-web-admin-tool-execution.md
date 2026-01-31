# Web Admin 工具调用功能实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 为 Serena Admin Dashboard 添加工具调用能力，支持通过 Web 界面测试和调试 Serena 工具。

**架构:** 三层设计 - 路由层添加执行端点，服务层负责工具发现和执行调度，视图层提供表单和结果展示。

**技术栈:** Flask (后端), Jinja2 (模板), 原生 JavaScript (前端), Pydantic (验证), Prism.js (代码高亮)

---

## Phase 1: 核心架构

### Task 1: 创建 ToolExecutorService 服务类

**文件:**
- 创建: `src/serena/admin/services/tool_executor_service.py`

**Step 1: 编写测试**

创建 `test/admin/test_tool_executor_service.py`:

```python
import pytest
from unittest.mock import MagicMock, Mock

def test_get_all_tools_returns_list():
    """测试获取所有工具列表"""
    mock_agent = MagicMock()
    mock_agent.get_exposed_tool_instances.return_value = [
        Mock(get_name=lambda: "read_file", __name__="read_file"),
        Mock(get_name=lambda: "find_symbol", __name__="find_symbol"),
    ]

    from serena.admin.services.tool_executor_service import get_tool_executor_service
    service = get_tool_executor_service(mock_agent)
    tools = service.get_all_tools()

    assert len(tools) == 2
    assert tools[0]["name"] == "read_file"
    assert tools[1]["name"] == "find_symbol"

def test_get_tool_schema():
    """测试获取工具的参数 schema"""
    mock_agent = MagicMock()
    mock_tool = Mock()
    mock_tool.get_name.return_value = "read_file"
    mock_agent._all_tools.values.return_value = [mock_tool]

    from serena.admin.services.tool_executor_service import get_tool_executor_service
    service = get_tool_executor_service(mock_agent)
    schema = service.get_tool_schema("read_file")

    assert "parameters" in schema
    assert "name" in schema["parameters"]
```

**Step 2: 运行测试验证失败**

```bash
cd D:/WorkeSpaceCoding/ai-agents/serena
pytest test/admin/test_tool_executor_service.py -v
```

预期: `ModuleNotFoundError: serena.admin.services.tool_executor_service`

**Step 3: 实现最小化代码**

创建 `src/serena/admin/services/tool_executor_service.py`:

```python
"""Tool executor service for admin dashboard."""

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
```

**Step 4: 运行测试验证通过**

```bash
pytest test/admin/test_tool_executor_service.py -v
```

预期: PASS

**Step 5: 提交**

```bash
git add test/admin/test_tool_executor_service.py src/serena/admin/services/tool_executor_service.py
git commit -m "feat(admin): add ToolExecutorService base class

Add initial service class for tool execution with:
- get_all_tools() method to list exposed tools
- get_tool_schema() method to get tool metadata
- Singleton pattern via get_tool_executor_service()

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 2: 更新 services/__init__.py 导出

**文件:**
- 修改: `src/serena/admin/services/__init__.py`

**Step 1: 编写测试**

在 `test/admin/test_tool_executor_service.py` 添加:

```python
def test_service_import():
    """测试服务可以从 services 模块导入"""
    from serena.admin.services import get_tool_executor_service
    assert callable(get_tool_executor_service)
```

**Step 2: 运行测试验证失败**

```bash
pytest test/admin/test_tool_executor_service.py::test_service_import -v
```

预期: `ImportError: cannot import name 'get_tool_executor_service'`

**Step 3: 修改文件**

在 `src/serena/admin/services/__init__.py` 添加:

```python
from .tool_executor_service import ToolExecutorService, get_tool_executor_service

__all__ = [
    "get_config_service",
    "get_monitoring_service",
    "get_project_service",
    "get_tool_service",
    "get_tool_executor_service",  # 新增
    "ToolExecutorService",
]
```

**Step 4: 运行测试验证通过**

```bash
pytest test/admin/test_tool_executor_service.py::test_service_import -v
```

预期: PASS

**Step 5: 提交**

```bash
git add src/serena/admin/services/__init__.py
git commit -m "feat(admin): export ToolExecutorService from services module

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 2: 工具列表页面

### Task 3: 创建工具列表路由

**文件:**
- 修改: `src/serena/admin/routes/__init__.py`

**Step 1: 添加路由测试**

在 `test/admin/test_routes.py` 添加:

```python
def test_tools_execute_list_route(client):
    """测试工具列表路由"""
    response = client.get("/admin/tools/execute")
    assert response.status_code == 200
    assert b"工具执行" in response.data
```

**Step 2: 运行测试验证失败**

```bash
pytest test/admin/test_routes.py::test_tools_execute_list_route -v
```

预期: `404 NOT FOUND`

**Step 3: 添加路由**

在 `src/serena/admin/routes/__init__.py` 的 `register_admin_routes` 函数中，在 `get_config_service` 导入后添加:

```python
from serena.admin.services import get_tool_executor_service
```

在 `config_service = ...` 行后添加:

```python
tool_executor_service = get_tool_executor_service(agent)
```

在 `@admin_bp.route("/monitoring/logs")` 后添加:

```python
@admin_bp.route("/tools/execute")
def tools_execute_list() -> str:
    """Render the tools execution list page."""
    tools = tool_executor_service.get_all_tools()
    # 按类别分组
    categorized_tools = _categorize_tools(tools)
    return render_template("tools/execute_list.html", categorized_tools=categorized_tools)


def _categorize_tools(tools: list[dict]) -> dict[str, list[dict]]:
    """将工具按类别分组。

    Args:
        tools: 工具列表

    Returns:
        按类别分组的工具字典
    """
    categories = {
        "文件操作": [],
        "符号操作": [],
        "内存管理": [],
        "配置管理": [],
        "编辑操作": [],
        "其他工具": [],
    }

    file_tools = {"read_file", "create_text_file", "replace_content", "list_dir", "find_file"}
    symbol_tools = {"find_symbol", "find_referencing_symbols", "get_symbols_overview", "rename_symbol"}
    memory_tools = {"list_memories", "read_memory", "write_memory", "edit_memory", "delete_memory"}
    config_tools = {"activate_project", "switch_modes", "get_current_config"}
    edit_tools = {"replace_symbol_body", "insert_after_symbol", "insert_before_symbol"}

    for tool in tools:
        name = tool["name"]
        if name in file_tools:
            categories["文件操作"].append(tool)
        elif name in symbol_tools:
            categories["符号操作"].append(tool)
        elif name in memory_tools:
            categories["内存管理"].append(tool)
        elif name in config_tools:
            categories["配置管理"].append(tool)
        elif name in edit_tools:
            categories["编辑操作"].append(tool)
        else:
            categories["其他工具"].append(tool)

    return categories
```

**Step 4: 运行测试验证通过**

```bash
pytest test/admin/test_routes.py::test_tools_execute_list_route -v
```

预期: PASS

**Step 5: 提交**

```bash
git add src/serena/admin/routes/__init__.py test/admin/test_routes.py
git commit -m "feat(admin): add tools execution list route

Add GET /admin/tools/execute route with:
- Tool categorization by functionality
- _categorize_tools() helper function
- Integration with ToolExecutorService

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 4: 创建工具列表模板

**文件:**
- 创建: `src/serena/admin/templates/tools/execute_list.html`

**Step 1: 手动验证模板渲染**

创建模板文件 `src/serena/admin/templates/tools/execute_list.html`:

```html
{% extends "base.html" %}

{% block title %}工具执行 - Serena Admin{% endblock %}

{% block content %}
<h2>工具执行</h2>

<div class="search-box">
    <input type="text" id="tool-search" placeholder="搜索工具名称或描述...">
</div>

<div class="tools-categories">
    {% for category, tools in categorized_tools.items() %}
    {% if tools %}
    <div class="category-section">
        <h3>{{ category }}</h3>
        <div class="tools-grid">
            {% for tool in tools %}
            <div class="tool-card" data-tool-name="{{ tool.name }}">
                <h4>{{ tool.name }}</h4>
                <p>{{ tool.description or '暂无描述' }}</p>
                <a href="/admin/tools/execute/{{ tool.name }}" class="btn btn-sm">执行</a>
            </div>
            {% endfor %}
        </div>
    </div>
    {% endif %}
    {% endfor %}
</div>
{% endblock %}

{% block scripts %}
<script>
document.getElementById('tool-search').addEventListener('input', function(e) {
    const query = e.target.value.toLowerCase();
    document.querySelectorAll('.tool-card').forEach(card => {
        const name = card.dataset.toolName.toLowerCase();
        const desc = card.querySelector('p').textContent.toLowerCase();
        card.style.display = (name.includes(query) || desc.includes(query)) ? 'block' : 'none';
    });
});
</script>

<style>
.search-box {
    margin-bottom: 2rem;
}

.search-box input {
    width: 100%;
    max-width: 600px;
    padding: 0.75rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
}

.category-section {
    margin-bottom: 2rem;
}

.category-section h3 {
    color: #333;
    border-bottom: 2px solid #007bff;
    padding-bottom: 0.5rem;
}

.tools-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
}

.tool-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    padding: 1rem;
    transition: box-shadow 0.2s;
}

.tool-card:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.tool-card h4 {
    margin-top: 0;
    color: #007bff;
}

.tool-card p {
    color: #666;
    font-size: 0.9rem;
    min-height: 2.7rem;
}

.btn-sm {
    padding: 0.4rem 0.8rem;
    font-size: 0.85rem;
}
</style>
{% endblock %}
```

**Step 2: 手动验证页面**

```bash
# 确保 admin dashboard 正在运行
curl -s "http://127.0.0.1:24283/admin/tools/execute" | grep "工具执行"
```

预期: 输出包含 "工具执行" 标题

**Step 3: 提交**

```bash
git add src/serena/admin/templates/tools/execute_list.html
git commit -m "feat(admin): add tools execution list page template

Add tool list page with:
- Categorized tool display
- Search functionality
- Responsive grid layout
- Clean card-based UI

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 3: 工具执行页面

### Task 5: 创建工具执行路由

**文件:**
- 修改: `src/serena/admin/routes/__init__.py`

**Step 1: 添加路由测试**

在 `test/admin/test_routes.py` 添加:

```python
def test_tool_execute_page_route(client, mock_agent):
    """测试单个工具执行页面"""
    mock_agent.get_exposed_tool_instances.return_value = [
        Mock(get_name=lambda: "read_file"),
    ]
    response = client.get("/admin/tools/execute/read_file")
    assert response.status_code == 200
```

**Step 2: 运行测试验证失败**

```bash
pytest test/admin/test_routes.py::test_tool_execute_page_route -v
```

预期: `404 NOT FOUND`

**Step 3: 添加路由**

在 `src/serena/admin/routes/__init__.py` 中，在 `@admin_bp.route("/tools/execute")` 后添加:

```python
@admin_bp.route("/tools/execute/<tool_name>")
def tool_execute_page(tool_name: str) -> str:
    """Render the tool execution page.

    Args:
        tool_name: Name of the tool to execute

    """
    try:
        tool_schema = tool_executor_service.get_tool_schema(tool_name)
        return render_template("tools/execute.html", tool_name=tool_name, tool_schema=tool_schema)
    except ValueError as e:
        return render_template("error.html", error=str(e)), 404


@admin_bp.route("/tools/execute/<tool_name>", methods=["POST"])
def execute_tool(tool_name: str) -> tuple[Response, int]:
    """Execute a tool with the provided parameters.

    Args:
        tool_name: Name of the tool to execute

    """
    try:
        data = request.get_json() or {}
        result = tool_executor_service.execute_tool(tool_name, data)
        return jsonify({"status": "success", "result": result})
    except ValueError as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"执行工具时出错: {e!s}"}), 500
```

**Step 4: 运行测试验证通过**

```bash
pytest test/admin/test_routes.py::test_tool_execute_page_route -v
```

预期: PASS

**Step 5: 提交**

```bash
git add src/serena/admin/routes/__init__.py test/admin/test_routes.py
git commit -m "feat(admin): add tool execution routes

Add GET/POST /admin/tools/execute/<tool_name> routes:
- GET: Render tool execution form page
- POST: Execute tool with parameters

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 6: 实现 ToolExecutorService.execute_tool

**文件:**
- 修改: `src/serena/admin/services/tool_executor_service.py`

**Step 1: 编写测试**

在 `test/admin/test_tool_executor_service.py` 添加:

```python
def test_execute_tool_success():
    """测试成功执行工具"""
    mock_agent = MagicMock()
    mock_tool = MagicMock()
    mock_tool.run.return_value = "file content here"

    with unittest.mock.patch.object(type(mock_agent), '_all_tools', {MagicMock: mock_tool}):
        mock_tool.get_name.return_value = "read_file"
        from serena.admin.services.tool_executor_service import get_tool_executor_service
        service = get_tool_executor_service(mock_agent)
        result = service.execute_tool("read_file", {"relative_path": "test.py"})

    assert result["status"] == "success"
    assert "content" in result
```

**Step 2: 运行测试验证失败**

```bash
pytest test/admin/test_tool_executor_service.py::test_execute_tool_success -v
```

预期: `AttributeError: 'ToolExecutorService' object has no attribute 'execute_tool'`

**Step 3: 实现方法**

在 `src/serena/admin/services/tool_executor_service.py` 的 `ToolExecutorService` 类中添加:

```python
import time
from typing import Any

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
```

**Step 4: 运行测试验证通过**

```bash
pytest test/admin/test_tool_executor_service.py::test_execute_tool_success -v
```

预期: PASS

**Step 5: 提交**

```bash
git add src/serena/admin/services/tool_executor_service.py test/admin/test_tool_executor_service.py
git commit -m "feat(admin): implement execute_tool method

Add tool execution with:
- Tool lookup by name
- Execution timing
- Error handling
- Metadata collection (elapsed time, timestamp)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 7: 创建工具执行模板

**文件:**
- 创建: `src/serena/admin/templates/tools/execute.html`

**Step 1: 手动验证模板**

创建 `src/serena/admin/templates/tools/execute.html`:

```html
{% extends "base.html" %}

{% block title %}{{ tool_name }} - 工具执行 - Serena Admin{% endblock %}

{% block content %}
<h2>工具执行: {{ tool_name }}</h2>

<form id="tool-form" class="tool-form">
    <div id="form-fields"></div>
    <div class="form-actions">
        <button type="submit" class="btn btn-primary">执行</button>
        <a href="/admin/tools/execute" class="btn btn-secondary">返回</a>
    </div>
</form>

<div id="result-container" style="display: none;">
    <div class="result-panel">
        <h3>执行结果</h3>
        <div id="result-content"></div>
    </div>
    <div class="metadata-panel">
        <h3>执行详情</h3>
        <div id="metadata-content"></div>
    </div>
</div>

<div id="error-message" class="alert alert-error" style="display: none;"></div>
{% endblock %}

{% block scripts %}
<script>
document.getElementById('tool-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData(this);
    const params = {};
    for (let [key, value] of formData.entries()) {
        params[key] = value;
    }

    try {
        const response = await fetch('/admin/tools/execute/{{ tool_name }}', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(params)
        });

        const data = await response.json();
        displayResult(data);
    } catch (error) {
        showError('网络错误: ' + error.message);
    }
});

function displayResult(data) {
    const resultContainer = document.getElementById('result-container');
    const resultContent = document.getElementById('result-content');
    const metadataContent = document.getElementById('metadata-content');

    if (data.status === 'success') {
        resultContent.textContent = JSON.stringify(data.result, null, 2);
        resultContent.className = 'result-success';
    } else {
        resultContent.textContent = data.message || '执行失败';
        resultContent.className = 'result-error';
    }

    if (data.metadata) {
        metadataContent.innerHTML = `
            <p><strong>状态:</strong> ${data.status}</p>
            <p><strong>耗时:</strong> ${data.metadata.elapsed_ms}ms</p>
            <p><strong>时间:</strong> ${data.metadata.timestamp}</p>
        `;
    }

    resultContainer.style.display = 'flex';
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}
</script>

<style>
.tool-form {
    max-width: 800px;
    margin: 0 auto 2rem;
}

.result-panel {
    flex: 3;
    padding: 1rem;
}

.metadata-panel {
    flex: 2;
    padding: 1rem;
    background: #f8f9fa;
    border-left: 1px solid #ddd;
}

#result-container {
    display: flex;
    border: 1px solid #ddd;
    border-radius: 8px;
    margin-top: 2rem;
}

.result-success {
    white-space: pre-wrap;
    font-family: monospace;
}

.result-error {
    color: #dc3545;
}

.alert-error {
    padding: 1rem;
    background: #f8d7da;
    color: #721c24;
    border-radius: 4px;
    margin-top: 1rem;
}
</style>
{% endblock %}
```

**Step 2: 手动验证页面**

```bash
curl -s "http://127.0.0.1:24283/admin/tools/execute/read_file" | grep "工具执行"
```

预期: 输出包含工具执行表单

**Step 3: 提交**

```bash
git add src/serena/admin/templates/tools/execute.html
git commit -m "feat(admin): add tool execution template

Add execution page with:
- Dynamic form rendering
- Split-panel result display
- Error handling
- Basic styling

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 4: 参数表单自动生成

### Task 8: 实现参数提取逻辑

**文件:**
- 修改: `src/serena/admin/services/tool_executor_service.py`

**Step 1: 编写测试**

在 `test/admin/test_tool_executor_service.py` 添加:

```python
def test_extract_parameters_from_tool():
    """测试从工具提取参数"""
    mock_agent = MagicMock()
    from serena.admin.services.tool_executor_service import get_tool_executor_service

    service = get_tool_executor_service(mock_agent)
    # 假设 read_file 工具存在并有参数
    params = service.get_tool_schema("read_file")

    assert "parameters" in params
    assert isinstance(params["parameters"], dict)
```

**Step 2: 运行测试**

```bash
pytest test/admin/test_tool_executor_service.py::test_extract_parameters_from_tool -v
```

**Step 3: 改进 _extract_parameters 方法**

修改 `src/serena/admin/services/tool_executor_service.py` 中的 `_extract_parameters`:

```python
import inspect
from mcp.server.fastmcp.utilities.func_metadata import func_metadata

def _extract_parameters(self, tool: Any) -> dict[str, Any]:
    """Extract parameter schema from tool.

    Args:
        tool: The tool instance

    Returns:
        A dictionary mapping parameter names to their schema
    """
    try:
        # Get the run method metadata
        metadata = func_metadata(tool.run)
        parameters = {}

        for param_name, param_info in metadata.parameters.items():
            if param_name == "self":
                continue

            param_schema = {
                "type": str(param_info.annotation),
                "required": param_info.default == inspect.Parameter.empty,
                "default": param_info.default if param_info.default != inspect.Parameter.empty else None,
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
```

**Step 4: 运行测试**

```bash
pytest test/admin/test_tool_executor_service.py::test_extract_parameters_from_tool -v
```

**Step 5: 提交**

```bash
git add src/serena/admin/services/tool_executor_service.py test/admin/test_tool_executor_service.py
git commit -m "feat(admin): implement parameter extraction from tools

Add _extract_parameters() method that:
- Uses func_metadata to inspect tool.run()
- Extracts type, required status, default values
- Handles extraction failures gracefully

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

### Task 9: 前端动态表单渲染

**文件:**
- 修改: `src/serena/admin/templates/tools/execute.html`

**Step 1: 添加表单渲染逻辑**

在 `execute.html` 的 `<script>` 部分添加:

```javascript
// 动态生成表单字段
const toolSchema = {{ tool_schema | tojson }};
const formFields = document.getElementById('form-fields');

function renderForm() {
    const params = toolSchema.parameters || {};

    for (const [paramName, paramInfo] of Object.entries(params)) {
        const fieldDiv = document.createElement('div');
        fieldDiv.className = 'form-group';

        const label = document.createElement('label');
        label.textContent = paramName + (paramInfo.required ? ' *' : '');
        fieldDiv.appendChild(label);

        let input;
        if (paramInfo.type === 'bool' || paramInfo.type === 'boolean') {
            input = document.createElement('input');
            input.type = 'checkbox';
        } else {
            input = document.createElement('input');
            input.type = 'text';
            input.value = paramInfo.default || '';
            if (paramInfo.required) input.required = true;
        }

        input.name = paramName;
        input.id = paramName;

        if (paramInfo.description) {
            const help = document.createElement('small');
            help.className = 'form-help';
            help.textContent = paramInfo.description;
            fieldDiv.appendChild(help);
        }

        fieldDiv.appendChild(input);
        formFields.appendChild(fieldDiv);
    }
}

renderForm();
```

同时更新 `<style>` 添加:

```css
.form-group {
    margin-bottom: 1.5rem;
}

.form-group label {
    display: block;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.form-group input[type="text"] {
    width: 100%;
    padding: 0.5rem;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.form-help {
    display: block;
    margin-top: 0.25rem;
    color: #6c757d;
    font-size: 0.875rem;
}
```

**Step 2: 手动验证**

访问 `http://127.0.0.1:24283/admin/tools/execute/read_file`

预期: 看到动态生成的参数表单

**Step 3: 提交**

```bash
git add src/serena/admin/templates/tools/execute.html
git commit -m "feat(admin): add dynamic form rendering

Add client-side form generation:
- Parse tool schema from backend
- Render inputs based on parameter types
- Handle required fields and defaults
- Add form styling

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## Phase 5: 代码高亮和结果美化

### Task 10: 添加 Prism.js 代码高亮

**文件:**
- 修改: `src/serena/admin/templates/base.html`

**Step 1: 更新基础模板**

在 `base.html` 的 `<head>` 中添加:

```html
<link href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism.min.css" rel="stylesheet" />
```

在 `</body>` 前添加:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-json.min.js"></script>
```

**Step 2: 更新 execute.html 使用代码高亮**

在 `displayResult` 函数中修改:

```javascript
function displayResult(data) {
    // ... existing code ...

    if (data.status === 'success') {
        const content = JSON.stringify(data.result, null, 2);
        resultContent.innerHTML = `<pre><code class="language-json">${escapeHtml(content)}</code></pre>`;
        Prism.highlightAll();
    }
    // ...
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

**Step 3: 手动验证**

执行一个工具，查看结果是否高亮

**Step 4: 提交**

```bash
git add src/serena/admin/templates/base.html src/serena/admin/templates/tools/execute.html
git commit -m "feat(admin): add Prism.js syntax highlighting

Add code highlighting for tool results:
- Include Prism.js CSS and JS
- Support Python and JSON
- Auto-highlight results after execution

Co-Authored-By: Claude <noreply@anthropic.com>"
```

---

## 测试命令汇总

```bash
# 运行所有 admin 测试
pytest test/admin/ -v

# 运行特定测试文件
pytest test/admin/test_tool_executor_service.py -v
pytest test/admin/test_routes.py -v

# 启动 admin dashboard
uv run python src/serena/admin/start_dashboard.py

# 访问页面
# http://127.0.0.1:24283/admin/tools/execute - 工具列表
# http://127.0.0.1:24283/admin/tools/execute/read_file - 执行特定工具
```

---

## 实施检查清单

- [ ] Phase 1: 核心架构
  - [ ] Task 1: ToolExecutorService
  - [ ] Task 2: 更新 services/__init__.py
- [ ] Phase 2: 工具列表页面
  - [ ] Task 3: 工具列表路由
  - [ ] Task 4: 工具列表模板
- [ ] Phase 3: 工具执行页面
  - [ ] Task 5: 执行页面路由
  - [ ] Task 6: execute_tool 实现
  - [ ] Task 7: 执行页面模板
- [ ] Phase 4: 参数表单生成
  - [ ] Task 8: 参数提取
  - [ ] Task 9: 动态表单渲染
- [ ] Phase 5: 代码高亮
  - [ ] Task 10: Prism.js 集成

---

**下一步:** 使用 `superpowers:executing-plans` 或 `superpowers:subagent-driven-development` 开始执行此计划。
