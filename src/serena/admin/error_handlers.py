"""Admin error handlers and utilities."""

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any

from flask import Flask, jsonify, render_template
from pydantic import ValidationError

if TYPE_CHECKING:
    from werkzeug.wrappers import Response


class AdminError(Exception):
    """Admin 模块基础异常"""

    def __init__(self, message: str, status_code: int = 400, error_code: str | None = None) -> None:
        """
        初始化 Admin 错误

        Args:
            message: 错误消息
            status_code: HTTP 状态码
            error_code: 错误代码

        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code


class ValidationErrorWrapper(AdminError):
    """验证错误包装器"""

    def __init__(self, errors: list[dict[str, Any]], status_code: int = 400) -> None:
        """
        初始化验证错误

        Args:
            errors: 验证错误列表
            status_code: HTTP 状态码

        """
        self.errors = errors
        message = "; ".join([f"{e.get('loc', ['未知'])}: {e.get('msg', '未知错误')}" for e in errors])
        super().__init__(message, status_code, "VALIDATION_ERROR")


def handle_validation_error(error: ValidationError) -> tuple["Response", int]:
    """
    处理 Pydantic 验证错误

    Args:
        error: Pydantic 验证错误

    Returns:
        JSON 错误响应和状态码

    """
    errors = error.errors()
    formatted_errors: list[dict[str, Any]] = []
    for err in errors:
        loc = " -> ".join(str(item) for item in err["loc"])
        formatted_errors.append(
            {
                "field": loc,
                "message": err["msg"],
                "type": err["type"],
            }
        )
    return (
        jsonify(
            {
                "status": "error",
                "message": "输入验证失败",
                "error_code": "VALIDATION_ERROR",
                "details": {"errors": formatted_errors},
            }
        ),
        400,
    )


def handle_admin_error(error: AdminError) -> tuple["Response", int]:
    """
    处理 Admin 错误

    Args:
        error: Admin 错误

    Returns:
        JSON 错误响应和状态码

    """
    response: dict[str, Any] = {
        "status": "error",
        "message": error.message,
    }
    if error.error_code:
        response["error_code"] = error.error_code
    return jsonify(response), error.status_code


def validate_request(model_class: type) -> Callable:
    """
    验证请求数据的装饰器

    Args:
        model_class: Pydantic 模型类

    Returns:
        装饰器函数

    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from flask import request

            try:
                data = request.get_json() or {}
                validated_data = model_class(**data)
                # 将验证后的数据作为关键字参数传递给原始函数
                return func(*args, validated_data=validated_data.model_dump(), **kwargs)
            except ValidationError as e:
                return handle_validation_error(e)
            except Exception as e:
                return (
                    jsonify(
                        {
                            "status": "error",
                            "message": f"请求处理失败: {e!s}",
                            "error_code": "REQUEST_ERROR",
                        }
                    ),
                    500,
                )

        return wrapper

    return decorator


def register_error_handlers(app: Flask) -> None:
    """
    注册全局错误处理器

    Args:
        app: Flask 应用实例

    """

    @app.errorhandler(ValidationError)
    def handle_pydantic_validation_error(error: ValidationError) -> tuple["Response", int]:
        """处理 Pydantic 验证错误"""
        return handle_validation_error(error)

    @app.errorhandler(AdminError)
    def handle_admin_custom_error(error: AdminError) -> tuple["Response", int]:
        """处理 Admin 自定义错误"""
        return handle_admin_error(error)

    @app.errorhandler(404)
    def handle_not_found(_error: Any) -> tuple[str, int]:
        """处理 404 错误 - 渲染错误页面"""
        return render_template("error.html", error_code=404, error_message="页面未找到"), 404

    @app.errorhandler(500)
    def handle_internal_error(_error: Any) -> tuple[str, int]:
        """处理 500 错误 - 渲染错误页面"""
        return render_template("error.html", error_code=500, error_message="服务器内部错误"), 500

    @app.errorhandler(403)
    def handle_forbidden(_error: Any) -> tuple[str, int]:
        """处理 403 错误 - 渲染错误页面"""
        return render_template("error.html", error_code=403, error_message="访问被禁止"), 403
