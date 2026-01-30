"""Pytest fixtures for admin route tests"""

from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
from flask import Flask

from serena.admin.routes import register_admin_routes

if TYPE_CHECKING:
    from flask.testing import FlaskClient


@pytest.fixture
def mock_agent() -> MagicMock:
    """创建模拟的 SerenaAgent 实例"""
    agent = MagicMock()

    # 模拟项目配置
    mock_project = MagicMock()
    mock_project.project_name = "test_project"
    mock_project.project_root = Path("/test/path")
    mock_project.project_config.languages = []
    mock_project.project_config.read_only = False

    # 模拟 serena_config
    agent.serena_config.projects = [mock_project]
    agent.get_active_project.return_value = mock_project

    # 模拟激活项目方法
    agent.activate_project_from_path_or_name.return_value = None

    return agent


@pytest.fixture
def app(mock_agent: MagicMock) -> Generator[Flask, None, None]:
    """创建 Flask 测试应用"""
    app = Flask(__name__)
    app.config["TESTING"] = True

    # 注册 admin 路由
    register_admin_routes(app, mock_agent)

    yield app


@pytest.fixture
def client(app: Flask) -> "FlaskClient":
    """创建 Flask 测试客户端"""
    return app.test_client()
