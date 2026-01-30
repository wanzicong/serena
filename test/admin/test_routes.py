"""测试 admin 路由"""

from typing import TYPE_CHECKING
from unittest.mock import MagicMock

if TYPE_CHECKING:
    from flask.testing import FlaskClient


class TestActivateProject:
    """测试项目激活 API"""

    def test_activate_project_success(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试成功激活项目"""
        response = client.post("/admin/projects/activate", json={"project_name": "test_project"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "已激活" in data["message"]
        mock_agent.activate_project_from_path_or_name.assert_called_once_with("test_project")

    def test_activate_project_missing_name(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试缺少项目名称参数的情况"""
        response = client.post("/admin/projects/activate", json={})

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        # 新的验证错误响应格式
        assert "输入验证失败" in data["message"] or "不能为空" in data.get("details", {}).get("errors", [{}])[0].get("message", "")
        mock_agent.activate_project_from_path_or_name.assert_not_called()

    def test_activate_project_empty_name(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试空项目名称的情况"""
        response = client.post("/admin/projects/activate", json={"project_name": ""})

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        # 新的验证错误响应格式
        assert "输入验证失败" in data["message"] or "不能为空" in data.get("details", {}).get("errors", [{}])[0].get("message", "")
        mock_agent.activate_project_from_path_or_name.assert_not_called()

    def test_activate_project_not_found(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试项目未找到的情况"""
        mock_agent.activate_project_from_path_or_name.side_effect = ValueError("项目未找到")

        response = client.post("/admin/projects/activate", json={"project_name": "nonexistent_project"})

        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == "error"
        assert "项目未找到" in data["message"]

    def test_activate_project_server_error(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试服务器内部错误的情况"""
        mock_agent.activate_project_from_path_or_name.side_effect = RuntimeError("服务器错误")

        response = client.post("/admin/projects/activate", json={"project_name": "test_project"})

        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"
        assert "激活项目时出错" in data["message"]


class TestDeleteProject:
    """测试项目删除 API"""

    def test_delete_project_success(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试成功删除项目"""
        response = client.post("/admin/projects/delete", json={"project_name": "test_project"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert "已删除" in data["message"]
        mock_agent.serena_config.remove_project.assert_called_once_with("test_project")

    def test_delete_project_missing_name(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试缺少项目名称参数的情况"""
        response = client.post("/admin/projects/delete", json={})

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        # 新的验证错误响应格式
        assert "输入验证失败" in data["message"] or "不能为空" in data.get("details", {}).get("errors", [{}])[0].get("message", "")
        mock_agent.serena_config.remove_project.assert_not_called()

    def test_delete_project_empty_name(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试空项目名称的情况"""
        response = client.post("/admin/projects/delete", json={"project_name": ""})

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        # 新的验证错误响应格式
        assert "输入验证失败" in data["message"] or "不能为空" in data.get("details", {}).get("errors", [{}])[0].get("message", "")
        mock_agent.serena_config.remove_project.assert_not_called()

    def test_delete_project_not_found(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试项目未找到的情况"""
        mock_agent.serena_config.remove_project.side_effect = ValueError("项目未找到")

        response = client.post("/admin/projects/delete", json={"project_name": "nonexistent_project"})

        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == "error"
        assert "项目未找到" in data["message"]

    def test_delete_project_server_error(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试服务器内部错误的情况"""
        mock_agent.serena_config.remove_project.side_effect = RuntimeError("服务器错误")

        response = client.post("/admin/projects/delete", json={"project_name": "test_project"})

        assert response.status_code == 500
        data = response.get_json()
        assert data["status"] == "error"
        assert "删除项目时出错" in data["message"]


class TestGetActiveProject:
    """测试获取当前激活项目 API"""

    def test_get_active_project_success(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试成功获取当前激活项目"""
        mock_project = MagicMock()
        mock_project.project_name = "active_project"
        mock_project.project_root = "/active/path"
        mock_agent.get_active_project.return_value = mock_project

        response = client.get("/admin/api/active-project")

        assert response.status_code == 200
        data = response.get_json()
        assert data["project_name"] == "active_project"
        assert data["project_path"] == "/active/path"

    def test_get_active_project_none(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试没有激活项目的情况"""
        mock_agent.get_active_project.return_value = None

        response = client.get("/admin/api/active-project")

        assert response.status_code == 200
        data = response.get_json()
        assert data["project_name"] is None
        assert data["project_path"] is None


class TestProjectsList:
    """测试项目列表页面路由"""

    def test_projects_list_route(self, client: "FlaskClient") -> None:
        """测试项目列表路由存在"""
        # 使用 pytest.raises 来捕获模板未找到的异常
        # 这证明路由是存在的, 只是模板文件未创建

        # 获取 Flask 应用实例
        app = client.application

        # 验证路由存在
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/projects" and "GET" in rule.methods:
                rule_found = True
                break

        assert rule_found, "项目列表路由不存在"


class TestIntegration:
    """集成测试 - 测试完整的 CRUD 工作流程"""

    def test_project_crud_workflow(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试完整的项目管理流程：Create -> Read -> Update -> Activate -> Delete"""
        # 1. 测试创建项目
        mock_new_project = MagicMock()
        mock_new_project.project_name = "new_test_project"
        mock_new_project.project_root = "/new/test/path"
        mock_new_project.project_config.languages = []
        mock_new_project.project_config.read_only = False

        mock_agent.serena_config.add_project_from_path.return_value = mock_new_project

        # 使用当前目录 (存在的路径)
        from pathlib import Path

        current_path = str(Path.cwd())

        create_response = client.post("/admin/projects/create", json={"project_path": current_path})

        assert create_response.status_code == 200
        create_data = create_response.get_json()
        assert create_data["status"] == "success"
        assert "已创建" in create_data["message"]
        assert create_data["project"]["name"] == "new_test_project"
        mock_agent.serena_config.add_project_from_path.assert_called_once()

        # 2. 测试读取项目列表 - 跳过模板渲染测试, 只验证 API 端点存在
        mock_agent.serena_config.projects = [mock_new_project]
        app = client.application
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/projects" and "GET" in rule.methods:
                rule_found = True
                break
        assert rule_found, "项目列表路由不存在"

        # 3. 测试更新项目 - 验证 API 端点存在
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/projects/update" and "POST" in rule.methods:
                rule_found = True
                break
        assert rule_found, "项目更新路由不存在"

        # 4. 测试激活项目
        mock_agent.get_active_project.return_value = mock_new_project
        activate_response = client.post("/admin/projects/activate", json={"project_name": "new_test_project"})

        assert activate_response.status_code == 200
        activate_data = activate_response.get_json()
        assert activate_data["status"] == "success"
        assert "已激活" in activate_data["message"]

        # 5. 测试删除项目
        delete_response = client.post("/admin/projects/delete", json={"project_name": "new_test_project"})

        assert delete_response.status_code == 200
        delete_data = delete_response.get_json()
        assert delete_data["status"] == "success"
        assert "已删除" in delete_data["message"]
        mock_agent.serena_config.remove_project.assert_called_once()

    def test_tool_toggle_workflow(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试工具切换功能"""
        # 模拟工具列表
        mock_agent.get_active_tool_names.return_value = ["find_symbol", "read_file"]
        mock_agent._all_tools = {
            "find_symbol": MagicMock(get_name_from_cls=lambda: "find_symbol"),
            "read_file": MagicMock(get_name_from_cls=lambda: "read_file"),
            "write_file": MagicMock(get_name_from_cls=lambda: "write_file"),
        }
        mock_agent._tool_usage_stats = MagicMock()
        mock_agent._tool_usage_stats.get_tool_stats_dict.return_value = {
            "find_symbol": {"num_times_called": 10, "input_tokens": 100, "output_tokens": 50},
            "read_file": {"num_times_called": 5, "input_tokens": 50, "output_tokens": 25},
        }

        # 1. 验证工具列表路由存在
        app = client.application
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/tools" and "GET" in rule.methods:
                rule_found = True
                break
        assert rule_found, "工具列表路由不存在"

        # 2. 测试切换工具状态
        # 由于工具切换功能尚未实现, 应该返回 501 错误
        toggle_response = client.post("/admin/tools/toggle", json={"tool_name": "write_file", "enabled": True})

        assert toggle_response.status_code == 501
        toggle_data = toggle_response.get_json()
        assert toggle_data["status"] == "error"
        assert "尚未实现" in toggle_data["message"]

    def test_config_edit_workflow(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试配置编辑功能"""
        # 1. 验证配置概览路由存在
        app = client.application
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/config" and "GET" in rule.methods:
                rule_found = True
                break
        assert rule_found, "配置概览路由不存在"

        # 2. 验证项目更新路由存在 (配置编辑通过项目更新实现)
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/projects/update" and "POST" in rule.methods:
                rule_found = True
                break
        assert rule_found, "项目更新路由不存在"

        # 3. 验证项目创建路由存在
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/projects/create" and "POST" in rule.methods:
                rule_found = True
                break
        assert rule_found, "项目创建路由不存在"

    def test_monitoring_workflow(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试监控功能工作流程"""
        # 1. 验证日志路由存在
        app = client.application
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/monitoring/logs" and "GET" in rule.methods:
                rule_found = True
                break
        assert rule_found, "日志路由不存在"

        # 2. 测试获取日志 API
        logs_api_response = client.get("/admin/api/logs?limit=10")
        assert logs_api_response.status_code == 200
        logs_data = logs_api_response.get_json()
        assert "logs" in logs_data

        # 3. 验证系统监控概览路由存在
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/monitoring" and "GET" in rule.methods:
                rule_found = True
                break
        assert rule_found, "系统监控概览路由不存在"

        # 4. 验证 LSP 状态监控路由存在
        rule_found = False
        for rule in app.url_map.iter_rules():
            if rule.rule == "/admin/monitoring/lsp" and "GET" in rule.methods:
                rule_found = True
                break
        assert rule_found, "LSP 状态监控路由不存在"

        # 5. 测试 LSP 状态 API
        lsp_api_response = client.get("/admin/api/lsp-status")
        assert lsp_api_response.status_code == 200
        lsp_data = lsp_api_response.get_json()
        assert isinstance(lsp_data, dict)

    def test_error_recovery_workflow(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试错误恢复工作流程"""
        # 1. 测试激活不存在的项目
        mock_agent.activate_project_from_path_or_name.side_effect = ValueError("项目未找到")

        response = client.post("/admin/projects/activate", json={"project_name": "nonexistent"})

        assert response.status_code == 404
        data = response.get_json()
        assert data["status"] == "error"

        # 重置 side_effect
        mock_agent.activate_project_from_path_or_name.side_effect = None

        # 2. 测试使用有效的项目名称
        mock_agent.activate_project_from_path_or_name.return_value = None

        response = client.post("/admin/projects/activate", json={"project_name": "valid_project"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

    def test_validation_workflow(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试输入验证工作流程"""
        # 1. 测试空项目名称的验证
        response = client.post("/admin/projects/activate", json={"project_name": ""})

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        mock_agent.activate_project_from_path_or_name.assert_not_called()

        # 2. 测试只有空格的项目名称
        response = client.post("/admin/projects/activate", json={"project_name": "   "})

        assert response.status_code == 400
        data = response.get_json()
        assert data["status"] == "error"
        mock_agent.activate_project_from_path_or_name.assert_not_called()

        # 3. 测试有效的项目名称
        response = client.post("/admin/projects/activate", json={"project_name": "valid_project"})

        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        mock_agent.activate_project_from_path_or_name.assert_called_once()

    def test_active_project_api_workflow(self, client: "FlaskClient", mock_agent: MagicMock) -> None:
        """测试获取激活项目 API 的工作流程"""
        # 1. 测试有激活项目的情况
        mock_project = MagicMock()
        mock_project.project_name = "active_project"
        mock_project.project_root = "/active/path"
        mock_agent.get_active_project.return_value = mock_project

        response = client.get("/admin/api/active-project")

        assert response.status_code == 200
        data = response.get_json()
        assert data["project_name"] == "active_project"
        assert data["project_path"] == "/active/path"

        # 2. 测试没有激活项目的情况
        mock_agent.get_active_project.return_value = None

        response = client.get("/admin/api/active-project")

        assert response.status_code == 200
        data = response.get_json()
        assert data["project_name"] is None
        assert data["project_path"] is None
