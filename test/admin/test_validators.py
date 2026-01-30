"""测试验证器和错误处理"""

from pathlib import Path

import pytest
from pydantic import ValidationError

from serena.admin.error_handlers import (
    AdminError,
    handle_admin_error,
    handle_validation_error,
)
from serena.admin.validators import (
    ErrorResponse,
    ProjectActionRequest,
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ToolToggleRequest,
)


class TestProjectCreateRequest:
    """测试 ProjectCreateRequest 验证器"""

    def test_valid_project_path(self, tmp_path: Path) -> None:
        """测试有效的项目路径"""
        valid_data = {
            "project_path": str(tmp_path),
        }
        request = ProjectCreateRequest(**valid_data)
        assert request.project_path == str(tmp_path.resolve())

    def test_project_path_expanduser(self) -> None:
        """测试用户路径展开"""
        # 使用当前目录的绝对路径
        valid_data = {
            "project_path": ".",
        }
        request = ProjectCreateRequest(**valid_data)
        assert Path(request.project_path).is_absolute()

    def test_empty_project_path(self) -> None:
        """测试空项目路径 - Pydantic 会先处理 min_length"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreateRequest(project_path="")
        errors = exc_info.value.errors()
        # Pydantic 的字段验证会先触发
        assert len(errors) > 0

    def test_whitespace_only_project_path(self) -> None:
        """测试只有空格的项目路径"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreateRequest(project_path="   ")
        errors = exc_info.value.errors()
        assert any("不能为空" in err["msg"] for err in errors)

    def test_nonexistent_project_path(self) -> None:
        """测试不存在的项目路径"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreateRequest(project_path="/nonexistent/path/12345")
        errors = exc_info.value.errors()
        assert any("不存在" in err["msg"] for err in errors)

    def test_valid_project_with_name(self, tmp_path: Path) -> None:
        """测试带项目名称的有效请求"""
        valid_data = {
            "project_path": str(tmp_path),
            "project_name": "TestProject",
        }
        request = ProjectCreateRequest(**valid_data)
        assert request.project_name == "TestProject"

    def test_project_name_too_long(self, tmp_path: Path) -> None:
        """测试过长的项目名称 - Pydantic 会先处理 max_length"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreateRequest(
                project_path=str(tmp_path),
                project_name="a" * 51,
            )
        errors = exc_info.value.errors()
        # 应该有验证错误
        assert len(errors) > 0

    def test_project_name_whitespace_only(self, tmp_path: Path) -> None:
        """测试只有空格的项目名称"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectCreateRequest(
                project_path=str(tmp_path),
                project_name="   ",
            )
        errors = exc_info.value.errors()
        assert any("不能只包含空格" in err["msg"] for err in errors)


class TestProjectUpdateRequest:
    """测试 ProjectUpdateRequest 验证器"""

    def test_valid_update_request(self) -> None:
        """测试有效的更新请求"""
        valid_data = {
            "project_name": "TestProject",
            "name": "NewProjectName",
            "description": "Test description",
        }
        request = ProjectUpdateRequest(**valid_data)
        assert request.project_name == "TestProject"
        assert request.name == "NewProjectName"
        assert request.description == "Test description"

    def test_whitespace_only_project_name(self) -> None:
        """测试只有空格的项目名称"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectUpdateRequest(project_name="   ")
        errors = exc_info.value.errors()
        assert any("不能为空" in err["msg"] or "不能只包含空格" in err["msg"] for err in errors)

    def test_description_too_long(self) -> None:
        """测试过长的描述 - Pydantic 会先处理 max_length"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectUpdateRequest(
                project_name="Test",
                description="a" * 501,
            )
        errors = exc_info.value.errors()
        # 应该有验证错误
        assert len(errors) > 0

    def test_new_name_whitespace_only(self) -> None:
        """测试只有空格的新名称"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectUpdateRequest(
                project_name="TestProject",
                name="   ",
            )
        errors = exc_info.value.errors()
        assert any("不能只包含空格" in err["msg"] for err in errors)


class TestProjectActionRequest:
    """测试 ProjectActionRequest 验证器"""

    def test_valid_action_request(self) -> None:
        """测试有效的操作请求"""
        valid_data = {"project_name": "TestProject"}
        request = ProjectActionRequest(**valid_data)
        assert request.project_name == "TestProject"

    def test_whitespace_only_project_name(self) -> None:
        """测试只有空格的项目名称"""
        with pytest.raises(ValidationError) as exc_info:
            ProjectActionRequest(project_name="   ")
        errors = exc_info.value.errors()
        assert any("不能为空" in err["msg"] or "不能只包含空格" in err["msg"] for err in errors)


class TestToolToggleRequest:
    """测试 ToolToggleRequest 验证器"""

    def test_valid_toggle_request(self) -> None:
        """测试有效的切换请求"""
        valid_data = {
            "tool_name": "test_tool",
            "enabled": True,
        }
        request = ToolToggleRequest(**valid_data)
        assert request.tool_name == "test_tool"
        assert request.enabled is True

    def test_valid_toggle_disabled(self) -> None:
        """测试禁用工具的请求"""
        valid_data = {
            "tool_name": "test_tool",
            "enabled": False,
        }
        request = ToolToggleRequest(**valid_data)
        assert request.tool_name == "test_tool"
        assert request.enabled is False

    def test_missing_enabled(self) -> None:
        """测试缺少 enabled 字段"""
        with pytest.raises(ValidationError) as exc_info:
            ToolToggleRequest(tool_name="test_tool")
        errors = exc_info.value.errors()
        assert any("enabled" in str(err.get("loc", [])) or "enabled" in str(err.get("type", "")) for err in errors)

    def test_whitespace_only_tool_name(self) -> None:
        """测试只有空格的工具名称"""
        with pytest.raises(ValidationError) as exc_info:
            ToolToggleRequest(tool_name="   ", enabled=True)
        errors = exc_info.value.errors()
        assert any("不能为空" in err["msg"] or "不能只包含空格" in err["msg"] for err in errors)


class TestErrorResponse:
    """测试 ErrorResponse 模型"""

    def test_error_response_default(self) -> None:
        """测试默认错误响应"""
        response = ErrorResponse(message="Test error")
        assert response.status == "error"
        assert response.message == "Test error"
        assert response.error_code is None
        assert response.details is None

    def test_error_response_full(self) -> None:
        """测试完整的错误响应"""
        response = ErrorResponse(
            message="Test error",
            error_code="TEST_ERROR",
            details={"field": "test"},
        )
        assert response.status == "error"
        assert response.message == "Test error"
        assert response.error_code == "TEST_ERROR"
        assert response.details == {"field": "test"}


class TestErrorHandlers:
    """测试错误处理器"""

    def test_admin_error(self) -> None:
        """测试 AdminError 异常"""
        error = AdminError("Test error", status_code=400, error_code="TEST_ERROR")
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.error_code == "TEST_ERROR"

    def test_admin_error_defaults(self) -> None:
        """测试 AdminError 默认值"""
        error = AdminError("Test error")
        assert error.status_code == 400
        assert error.error_code is None

    def test_handle_validation_error(self, app) -> None:
        """测试验证错误处理"""
        # 创建一个验证错误
        try:
            ProjectCreateRequest(project_path="   ")
        except ValidationError as e:
            with app.app_context():
                response, status_code = handle_validation_error(e)
                # 验证返回的是 Response 对象和正确的状态码
                assert status_code == 400
                assert response.content_type == "application/json"
                # 验证响应体包含错误信息
                import json

                data = json.loads(response.get_data(as_text=True))
                assert data["status"] == "error"
                assert "输入验证失败" in data["message"] or "VALIDATION_ERROR" in data.get("error_code", "")

    def test_handle_admin_error(self, app) -> None:
        """测试 Admin 错误处理"""
        error = AdminError("Test error", status_code=404, error_code="NOT_FOUND")
        with app.app_context():
            response, status_code = handle_admin_error(error)
            # 验证返回的是 Response 对象和正确的状态码
            assert status_code == 404
            assert response.content_type == "application/json"
            # 验证响应体包含错误信息
            import json

            data = json.loads(response.get_data(as_text=True))
            assert data["status"] == "error"
            assert data["message"] == "Test error"
            assert data.get("error_code") == "NOT_FOUND"
