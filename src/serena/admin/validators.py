"""Admin input validators using Pydantic."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class ProjectCreateRequest(BaseModel):
    """验证项目创建请求"""

    project_path: str = Field(..., min_length=1, description="项目路径")
    project_name: str | None = Field(None, min_length=1, max_length=50, description="项目名称")

    @field_validator("project_path")
    @classmethod
    def validate_project_path(cls, v: str) -> str:
        """
        验证项目路径

        Args:
            v: 项目路径

        Returns:
            验证后的路径

        Raises:
            ValueError: 如果路径为空或格式无效

        """
        if not v or not v.strip():
            raise ValueError("项目路径不能为空")
        # 展开用户路径 (e.g. ~)
        expanded = Path(v).expanduser()
        if not expanded.exists():
            raise ValueError(f"项目路径不存在: {v}")
        return str(expanded.resolve())

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str | None) -> str | None:
        """
        验证项目名称

        Args:
            v: 项目名称

        Returns:
            验证后的名称

        Raises:
            ValueError: 如果名称格式无效

        """
        if v is not None:
            if not v.strip():
                raise ValueError("项目名称不能只包含空格")
            if len(v) > 50:
                raise ValueError("项目名称不能超过50个字符")
        return v


class ProjectUpdateRequest(BaseModel):
    """验证项目更新请求"""

    project_name: str = Field(..., min_length=1, description="项目名称")
    name: str | None = Field(None, min_length=1, max_length=50, description="新的项目名称")
    description: str | None = Field(None, max_length=500, description="项目描述")
    language: str | None = Field(None, description="项目语言")

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """
        验证项目名称

        Args:
            v: 项目名称

        Returns:
            验证后的名称

        Raises:
            ValueError: 如果名称为空

        """
        if not v or not v.strip():
            raise ValueError("项目名称不能为空")
        return v

    @field_validator("name")
    @classmethod
    def validate_new_name(cls, v: str | None) -> str | None:
        """
        验证新的项目名称

        Args:
            v: 新的项目名称

        Returns:
            验证后的名称

        Raises:
            ValueError: 如果名称格式无效

        """
        if v is not None:
            if not v.strip():
                raise ValueError("新的项目名称不能只包含空格")
            if len(v) > 50:
                raise ValueError("项目名称不能超过50个字符")
        return v

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str | None) -> str | None:
        """
        验证项目描述

        Args:
            v: 项目描述

        Returns:
            验证后的描述

        Raises:
            ValueError: 如果描述过长

        """
        if v is not None and len(v) > 500:
            raise ValueError("项目描述不能超过500个字符")
        return v


class ProjectActionRequest(BaseModel):
    """验证项目操作请求（激活、删除等）"""

    project_name: str = Field(..., min_length=1, description="项目名称")

    @field_validator("project_name")
    @classmethod
    def validate_project_name(cls, v: str) -> str:
        """
        验证项目名称

        Args:
            v: 项目名称

        Returns:
            验证后的名称

        Raises:
            ValueError: 如果名称为空

        """
        if not v or not v.strip():
            raise ValueError("项目名称不能为空")
        return v


class ToolToggleRequest(BaseModel):
    """验证工具切换请求"""

    tool_name: str = Field(..., min_length=1, description="工具名称")
    enabled: bool | None = Field(..., description="是否启用")

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        """
        验证工具名称

        Args:
            v: 工具名称

        Returns:
            验证后的名称

        Raises:
            ValueError: 如果名称为空

        """
        if not v or not v.strip():
            raise ValueError("工具名称不能为空")
        return v

    @model_validator(mode="after")
    def validate_enabled_field(self) -> "ToolToggleRequest":
        """
        验证 enabled 字段存在

        Returns:
            验证后的请求

        Raises:
            ValueError: 如果 enabled 未提供

        """
        if self.enabled is None:
            raise ValueError("必须指定 enabled 状态")
        return self


class ErrorResponse(BaseModel):
    """错误响应模型"""

    status: str = Field(default="error", description="状态，始终为 'error'")
    message: str = Field(..., description="错误消息")
    error_code: str | None = Field(None, description="错误代码")
    details: dict[str, Any] | None = Field(None, description="错误详情")
