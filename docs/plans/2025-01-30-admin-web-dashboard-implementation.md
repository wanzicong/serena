# Serena 管理后台 Web 化实施计划

> **For Claude:** REQUIRED SUBKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**目标:** 为 Serena 添加一个基于 Web 的管理后台，支持项目管理、工具管理、配置编辑和系统监控功能，将 MCP 命令行操作迁移到可视化界面。

**Architecture:** 扩展现有 Flask Dashboard，添加 `/admin` 路由，使用 Jinja2 模板渲染，通过直接读写 YAML 配置文件实现数据持久化，与现有系统无缝集成。

**Tech Stack:** Flask 3.x、Jinja2、原生 JavaScript、Pydantic（输入验证）

---

## Task 1: 创建 Admin 模块基础结构

**Files:**
- Create: `src/serena/admin/__init__.py`
- Create: `src/serena/admin/routes/__init__.py`
- Create: `src/serena/admin/templates/base.html`

**Step 1: Create admin package init file**

```python
# src/serena/admin/__init__.py
"""Serena Admin Dashboard - Web UI for Serena management"""

__version__ = "0.1.0"
```

**Step 2: Create routes package init file**

```python
# src/serena/admin/routes/__init__.py
"""Admin route definitions"""
```

**Step 3: Create base template**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Serena Admin{% endblock %}</title>
    <link rel="stylesheet" href="/admin/static/admin.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-brand">
            <h1>Serena Admin</h1>
        </div>
        <ul class="nav-links">
            <li><a href="/admin/projects">项目</a></li>
            <li><a href="/admin/tools">工具</a></li>
            <li><a href="/admin/config">配置</a></li>
            <li><a href="/admin/monitoring">监控</a></li>
        </ul>
        <div class="nav-right">
            <span id="active-project">加载中...</span>
        </div>
    </nav>
    
    <main class="container">
        {% block content %}{% endblock %}
    </main>
    
    <script src="/admin/static/admin.js"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

**Step 4: Commit**

```bash
git add src/serena/admin/
git commit -m "feat(admin): add admin module base structure and base template"
```

---

## Task 2: 集成 Admin 路由到主应用

**Files:**
- Modify: `src/serena/dashboard.py`

**Step 1: Register admin routes in main app**

在 `SerenaDashboardAPI._setup_routes()` 方法末尾添加：

```python
from serena.admin.routes import register_admin_routes

# Inside _setup_routes method, after all existing routes
register_admin_routes(self._app, self._agent)
```

**Step 2: Run and verify**

Run: `uv run serena-mcp-server --project .`
Visit: `http://localhost:8000/admin/`

Expected: 404 页面（因为路由还未实现）但 Flask 应用正常启动

**Step 3: Commit**

```bash
git add src/serena/dashboard.py
git commit -m "feat(admin): integrate admin routes into main Flask app"
```

---

## Task 3: 实现项目管理 - 项目列表页面

**Files:**
- Create: `src/serena/admin/services/project_service.py`
- Create: `src/serena/admin/routes.py`
- Create: `src/serena/admin/templates/projects/list.html`
- Create: `src/serena/admin/static/admin.css`
- Create: `src/serena/admin/static/admin.js`

**Step 1: Create project service**

```python
# src/serena/admin/services/project_service.py
"""Project management business logic"""

from typing import List, Dict, Any
from serena.config.serena_config import SerenaConfig

class ProjectService:
    def __init__(self, agent):
        self._agent = agent
    
    def get_all_projects(self) -> List[Dict[str, Any]]:
        """Get all registered projects with their details"""
        projects = []
        active_project = self._agent.get_active_project()
        
        for proj in self._agent.serena_config.projects:
            is_active = active_project and active_project.project_name == proj.project_name
            
            # Get languages
            languages = [lang.value for lang in proj.project_config.languages]
            
            projects.append({
                'name': proj.project_name,
                'path': str(proj.project_root),
                'languages': languages,
                'is_active': is_active,
                'read_only': proj.project_config.read_only
            })
        
        return projects
    
    def activate_project(self, project_name: str) -> None:
        """Activate a project by name"""
        self._agent.activate_project_from_path_or_name(project_name)
    
    def delete_project(self, project_name: str) -> None:
        """Delete a project by name"""
        # Implement deletion logic
        config = self._agent.serena_config
        config.remove_project(project_name)
```

**Step 2: Create admin routes**

```python
# src/serena/admin/routes.py
"""Admin dashboard routes"""

from flask import Blueprint, render_template, request, jsonify
from serena.admin.services.project_service import ProjectService

def register_admin_routes(app, agent):
    """Register all admin routes with the Flask app"""
    
    bp = Blueprint('admin', __name__, url_prefix='/admin')
    project_service = ProjectService(agent)
    
    @bp.route('/projects')
    def projects_list():
        projects = project_service.get_all_projects()
        return render_template('projects/list.html', projects=projects)
    
    app.register_blueprint(bp)
```

**Step 3: Create projects list template**

```html
<!-- src/serena/admin/templates/projects/list.html -->
{% extends "base.html" %}

{% block title %}项目管理 - Serena Admin{% endblock %}

{% block content %}
<h2>项目管理</h2>
<table class="data-table">
    <thead>
        <tr>
            <th>项目名称</th>
            <th>路径</th>
            <th>语言</th>
            <th>状态</th>
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        {% for project in projects %}
        <tr class="{{ 'active' if project.is_active else '' }}">
            <td>{{ project.name }}</td>
            <td><code>{{ project.path }}</code></td>
            <td>{{ project.languages | join(', ') }}</td>
            <td>
                {% if project.is_active %}
                <span class="badge badge-success">活跃</span>
                {% else %}
                    <span class="badge badge-secondary">未激活</span>
                {% endif %}
            </td>
            <td>
                {% if not project.is_active %}
                <button onclick="activateProject('{{ project.name }}')">激活</button>
                {% endif %}
                <button onclick="editProject('{{ project.name }}')">编辑</button>
                <button onclick="deleteProject('{{ project.name }}')" class="danger">删除</button>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>

<div class="actions">
    <a href="/admin/projects/new" class="btn btn-primary">添加新项目</a>
</div>
{% endblock %}
```

**Step 4: Create basic styles**

```css
/* src/serena/admin/static/admin.css */
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #f5f5f5;
    color: #333;
}

.navbar {
    background: #2c3e50;
    color: white;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.nav-brand h1 { font-size: 1.2rem; margin: 0; }
.nav-links { display: flex; gap: 2rem; list-style: none; }
.nav-links a { color: white; text-decoration: none; }
.nav-links a:hover { opacity: 0.8; }

.container { max-width: 1200px; margin: 0 auto; padding: 2rem; }

.data-table { width: 100%; border-collapse: collapse; margin: 2rem 0; }
.data-table th { background: #34495e; color: white; text-align: left; padding: 0.75rem; }
.data-table td { border-bottom: 1px solid #ddd; padding: 0.75rem; }
.data-table tr:hover { background: #f8f9fa; }

.badge { padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.875rem; }
.badge-success { background: #28a745; color: white; }
.badge-secondary { background: #6c757d; color: white; }

button { padding: 0.375rem 0.75rem; border: none; border-radius: 4px; cursor: pointer; margin-right: 0.25rem; }
.btn-primary { background: #007bff; color: white; }
.danger { background: #dc3545; color: white; }
.btn { display: inline-block; text-decoration: none; }

.actions { margin: 2rem 0; }
```

**Step 5: Create basic JavaScript**

```javascript
// src/serena/admin/static/admin.js

// 项目操作
function activateProject(name) {
    if (confirm(`确定要激活项目 "${name}" 吗？`)) {
        fetch('/admin/projects/activate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_name: name })
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('success', data.message);
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast('error', data.message);
            }
        });
    }
}

function editProject(name) {
    window.location.href = `/admin/projects/${name}/edit`;
}

function deleteProject(name) {
    if (confirm(`确定要删除项目 "${name}" 吗？此操作不可撤销。`)) {
        fetch('/admin/projects/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ project_name: name })
        })
        .then(r => r.json())
        .then(data => {
            if (data.status === 'success') {
                showToast('success', data.message);
                setTimeout(() => location.reload(), 1000);
            } else {
                showToast('error', data.message);
            }
        });
    }
}

// Toast 通知
function showToast(type, message) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => toast.remove(), 3000);
}
```

**Step 6: Run and verify**

Run: `uv run serena-mcp-server --project .`
Visit: `http://localhost:8000/admin/projects`

Expected: 显示项目列表页面（如果没有任何项目，显示空列表）

**Step 7: Commit**

```bash
git add src/serena/admin/
git commit -m "feat(admin): implement projects list page with basic UI"
```

---

## Task 4: 实现项目激活功能

**Files:**
- Modify: `src/serena/admin/routes.py`
- Create: `test/admin/test_routes.py`

**Step 1: Add activate route**

```python
@bp.route('/projects/activate', methods=['POST'])
def activate_project():
    data = request.get_json()
    project_name = data.get('project_name')
    
    if not project_name:
        return jsonify({'status': 'error', 'message': '缺少项目名称'})
    
    try:
        project_service.activate_project(project_name)
        return jsonify({'status': 'success', 'message': f'项目 {project_name} 已激活'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
```

**Step 2: Write test**

```python
# test/admin/test_routes.py
import pytest

def test_activate_project(client, mock_agent):
    """测试项目激活 API"""
    mock_agent.activate_project_from_path_or_name.return_value = None
    
    response = client.post('/admin/projects/activate', 
                           json={'project_name': 'test_project'})
    
    assert response.status_code == 200
    data = response.json
    assert data['status'] == 'success'
    mock_agent.activate_project_from_path_or_name.assert_called_once_with('test_project')
```

**Step 3: Run tests**

Run: `pytest test/admin/test_routes.py::test_activate_project -v`

**Step 4: Commit**

```bash
git add src/serena/admin/routes.py test/admin/
git commit -m "feat(admin): add project activation endpoint"
```

---

## Task 5: 实现工具管理页面

**Files:**
- Create: `src/serena/admin/services/tool_service.py`
- Modify: `src/serena/admin/routes.py`
- Create: `src/serena/admin/templates/tools/list.html`

**Step 1: Create tool service**

```python
# src/serena/admin/services/tool_service.py

class ToolService:
    def __init__(self, agent):
        self._agent = agent
    
    def get_all_tools(self):
        """Get all tools with their status"""
        tools = []
        active_tools = self._agent.get_active_tool_names()
        all_tool_names = sorted([
            tool.get_name_from_cls() 
            for tool in self._agent._all_tools.values()
        ])
        
        for tool_name in all_tool_names:
            tools.append({
                'name': tool_name,
                'is_active': tool_name in active_tools,
                'calls': self._get_tool_call_count(tool_name)
            })
        
        return tools
    
    def _get_tool_call_count(self, tool_name: str) -> int:
        """Get tool call count from stats"""
        if self._agent._tool_usage_stats:
            stats = self._agent._tool_usage_stats.get_tool_stats_dict()
            return stats.get(tool_name, {}).get('num_times_called', 0)
        return 0
    
    def toggle_tool(self, tool_name: str, enabled: bool):
        """Toggle tool enabled/disabled"""
        # Implementation will modify project config
        pass
```

**Step 2: Add tools route and template**

```python
@bp.route('/tools')
def tools_list():
    tools = tool_service.get_all_tools()
    return render_template('tools/list.html', tools=tools)
```

**Step 3: Run and verify**

Visit: `http://localhost:8000/admin/tools`

**Step 4: Commit**

```bash
git add src/serena/admin/services/tool_service.py
git commit -m "feat(admin): add tools management page"
```

---

## Task 6: 实现配置管理页面

**Files:**
- Create: `src/serena/admin/services/config_service.py`
- Modify: `src/serena/admin/routes.py`
- Create: `src/serena/admin/templates/config/overview.html`

**Step 1: Create config service**

```python
# src/serena/admin/services/config_service.py

class ConfigService:
    def __init__(self, agent):
        self._agent = agent
    
    def get_config_overview(self):
        """Get configuration overview"""
        return self._agent.get_current_config_overview()
    
    def save_serena_config(self, content: str) -> None:
        """Save serena config YAML"""
        import os
        config_path = self._agent.serena_config.config_file_path
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
```

**Step 2: Add config routes and template**

**Step 3: Run and verify**

Visit: `http://localhost:8000/admin/config`

**Step 4: Commit**

```bash
git add src/serena/admin/services/config_service.py
git commit -m "feat(admin): add config management page"
```

---

## Task 7: 实现系统监控页面

**Files:**
- Create: `src/serena/admin/services/monitoring_service.py`
- Modify: `src/serena/admin/routes.py`
- Create: `src/serena/admin/templates/monitoring/overview.html`

**Step 1: Create monitoring service**

```python
# src/serena/admin/services/monitoring_service.py

class MonitoringService:
    def __init__(self, agent):
        self._agent = agent
    
    def get_system_status(self):
        """Get overall system status"""
        lsp_languages = self._agent.get_active_lsp_languages()
        current_tasks = self._agent.get_current_tasks()
        
        return {
            'lsp_servers': len(lsp_languages),
            'active_tasks': len(current_tasks),
            'active_project': self._agent.get_active_project_or_raise().project_name if self._agent.get_active_project() else None
        }
```

**Step 2: Add monitoring routes**

**Step 3: Run and verify**

Visit: `http://localhost:8000/admin/monitoring`

**Step 4: Commit**

```bash
git add src/serena/admin/services/monitoring_service.py
git commit -m "feat(admin): add system monitoring overview page"
```

---

## Task 8: 实现日志查看器

**Files:**
- Modify: `src/serena/admin/routes.py`
- Create: `src/serena/admin/templates/monitoring/logs.html`
- Modify: `src/serena/admin/static/admin.js` (add log streaming)

**Step 1: Add logs route**

```python
@bp.route('/monitoring/logs')
def logs_page():
    return render_template('monitoring/logs.html')
```

**Step 2: Add WebSocket log streaming**

**Step 3: Run and verify**

Visit: `http://localhost:8000/admin/monitoring/logs`

**Step 4: Commit**

```bash
git add src/serena/admin/routes.py
git commit -m "feat(admin): add log viewer with real-time streaming"
```

---

## Task 9: 实现项目创建页面

**Files:**
- Create: `src/serena/admin/templates/projects/new.html`

**Step 1: Create new project form**

**Step 2: Add form submission handler**

**Step 3: Run and verify**

**Step 4: Commit**

```bash
git add src/serena/admin/templates/projects/new.html
git commit -m "feat(admin): add create new project page"
```

---

## Task 10: 实现项目编辑页面

**Files:**
- Create: `src/serena/admin/templates/projects/detail.html`

**Step 1: Create project detail/edit page**

**Step 2: Add update route**

**Step 3: Run and verify**

**Step 4: Commit**

```bash
git add src/serena/admin/templates/projects/detail.html
git commit -m "feat(admin): add project detail and edit page"
```

---

## Task 11: 实现工具统计页面

**Files:**
- Create: `src/serena/admin/templates/tools/stats.html`

**Step 1: Create stats page with charts**

**Step 2: Add stats route**

**Step 3: Run and verify**

**Step 4: Commit**

```bash
git add src/serena/admin/templates/tools/stats.html
git commit -m "feat(admin): add tool usage statistics page"
```

---

## Task 12: 实现 LSP 状态监控

**Files:**
- Create: `src/serena/admin/templates/monitoring/lsp.html`

**Step 1: Create LSP status page**

**Step 2: Add LSP monitoring service methods**

**Step 3: Run and verify**

**Step 4: Commit**

```bash
git add src/serena/admin/templates/monitoring/lsp.html
git commit -m "feat(admin): add LSP server status monitoring page"
```

## Task 13: 实现 Toast 通知系统

**Files:**
- Modify: `src/serena/admin/static/admin.css`
- Modify: `src/serena/admin/static/admin.js`

**Step 1: Add Toast styles and animations**

**Step 2: Implement showToast function improvements**

**Step 3: Test notifications across all pages**

**Step 4: Commit**

```bash
git add src/serena/admin/static/
git commit -m "feat(admin): implement toast notification system"
```

---

## Task 14: 添加错误处理和验证

**Files:**
- Create: `src/serena/admin/validators.py`
- Modify: `src/serena/admin/routes.py`
- Create: `src/serena/admin/templates/error.html`

**Step 1: Create input validators using Pydantic**

```python
# src/serena/admin/validators.py

from pydantic import BaseModel, Field, validator

class ProjectCreateRequest(BaseModel):
    path: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1, max_length=50)
```

**Step 2: Add error handler**

**Step 3: Test error handling**

**Step 4: Commit**

```bash
git add src/serena/admin/validators.py
git commit -m "feat(admin): add input validation and error handling"
```

---

## Task 15: 编写集成测试

**Files:**
- Modify: `test/admin/test_routes.py`

**Step 1: Add comprehensive integration tests**

```python
def test_project_crud_workflow():
    """测试完整的项目管理流程"""
    # Create -> Read -> Update -> Activate -> Delete
    pass

def test_tool_toggle_workflow():
    """测试工具切换功能"""
    pass

def test_config_edit_workflow():
    """测试配置编辑功能"""
    pass
```

**Step 2: Run all tests**

Run: `pytest test/admin/ -v`

**Step 3: Commit**

```bash
git add test/admin/
git commit -m "test(admin): add comprehensive integration tests"
```

---

## Task 16: 添加样式和用户体验优化

**Files:**
- Modify: `src/serena/admin/static/admin.css`
- Modify: `src/serena/admin/static/admin.js`

**Step 1: Enhance CSS with modern design**

**Step 2: Add loading states and animations**

**Step 3: Test in browser**

**Step 4: Commit**

```bash
git add src/serena/admin/static/
git commit -m "style(admin): enhance UI with modern design and animations"
```

---

## Task 17: 编写使用文档

**Files:**
- Create: `docs/admin-guide.md`

**Step 1: Create admin usage guide**

**Step 2: Document available features**

**Step 3: Commit**

```bash
git add docs/admin-guide.md
git commit -m "docs(admin): add admin dashboard usage guide"
```

---

## Task 18: 最终测试和发布

**Files:**
- Modify: `src/serena/dashboard.py` (if needed)

**Step 1: End-to-end testing**

Run: `uv run serena-mcp-server --project .`
- Test all admin pages
- Verify all CRUD operations
- Check error handling

**Step 2: Performance check**

- Test with multiple projects
- Check page load times
- Verify memory usage

**Step 3: Final commit**

```bash
git add .
git commit -m "feat(admin): complete admin web dashboard implementation"
```

---

## 总结

本实施计划包含 **18 个任务**，涵盖：

1. ✅ 基础架构搭建
2. ✅ 项目管理（列表、创建、编辑、删除、激活）
3. ✅ 工具管理（列表、切换、统计）
4. ✅ 配置管理（查看、编辑）
5. ✅ 系统监控（总览、LSP、日志、任务）
6. ✅ 错误处理和验证
7. ✅ 测试覆盖
8. ✅ UI/UX 优化
9. ✅ 文档完善

**预计开发时间**: 约 2-4 小时（如果按步骤执行）

**技术债务**: 未来可考虑的功能
- WebSocket 实时日志
- 高级搜索和过滤
- 用户认证
- 多语言支持
- 深度性能分析
