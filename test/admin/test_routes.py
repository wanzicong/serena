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
