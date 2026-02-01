"""Admin route definitions"""

from pathlib import Path
from typing import TYPE_CHECKING

from flask import Blueprint, Flask, Response, jsonify, render_template, request
from pydantic import ValidationError

from serena.admin.error_handlers import register_error_handlers
from serena.admin.services import (
    get_config_service,
    get_monitoring_service,
    get_project_service,
    get_tool_executor_service,
    get_tool_service,
)
from serena.admin.validators import (
    ProjectActionRequest,
    ProjectCreateRequest,
    ProjectUpdateRequest,
    ToolToggleRequest,
)

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


def register_admin_routes(app: Flask, agent: "SerenaAgent") -> None:
    """
    Register admin routes with the Flask application.

    Args:
        app: The Flask application instance
        agent: The SerenaAgent instance

    """
    # 注册错误处理器
    register_error_handlers(app)

    # 获取 admin 模块的路径来配置静态文件夹
    from serena.admin import __file__ as admin_init_file
    admin_static_dir = str(Path(admin_init_file).parent / "static")

    # Create a blueprint for admin routes (配置静态文件夹)
    admin_bp = Blueprint("admin", __name__, url_prefix="/admin", static_folder=admin_static_dir, static_url_path="/admin/static")

    # Get service instances
    config_service = get_config_service(agent)
    project_service = get_project_service(agent)
    tool_service = get_tool_service(agent)
    monitoring_service = get_monitoring_service(agent)
    tool_executor_service = get_tool_executor_service(agent)

    @admin_bp.route("/")
    def admin_home() -> str:
        """Render the admin home page."""
        return render_template("index.html")

    @admin_bp.route("/projects")
    def projects_list() -> str:
        """Render the projects list page."""
        projects = project_service.get_all_projects()
        return render_template("projects/list.html", projects=projects)

    @admin_bp.route("/projects/activate", methods=["POST"])
    def activate_project() -> tuple[Response, int] | Response:
        """Activate a project by name."""
        try:
            data = request.get_json() or {}
            validated = ProjectActionRequest(**data)
            project_service.activate_project(validated.project_name)
            return jsonify({"status": "success", "message": f"项目 '{validated.project_name}' 已激活"})
        except ValidationError:
            # 验证错误由全局错误处理器处理
            raise
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": f"激活项目时出错: {e!s}"}), 500

    @admin_bp.route("/projects/delete", methods=["POST"])
    def delete_project() -> tuple[Response, int] | Response:
        """Delete a project by name."""
        try:
            data = request.get_json() or {}
            validated = ProjectActionRequest(**data)
            project_service.delete_project(validated.project_name)
            return jsonify({"status": "success", "message": f"项目 '{validated.project_name}' 已删除"})
        except ValidationError:
            # 验证错误由全局错误处理器处理
            raise
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": f"删除项目时出错: {e!s}"}), 500

    @admin_bp.route("/projects/new")
    def projects_new() -> str:
        """Render the new project creation page."""
        languages = project_service.get_available_languages()
        return render_template("projects/new.html", languages=languages)

    @admin_bp.route("/projects/browse-filesystem", methods=["POST"])
    def browse_filesystem() -> tuple[Response, int] | Response:
        """Browse the filesystem and return directory contents."""
        import os
        import platform

        try:
            data = request.get_json() or {}
            path = data.get("path", "")

            # 如果没有提供路径，返回根目录或驱动器列表
            if not path:
                system = platform.system()
                if system == "Windows":
                    # Windows: 返回所有驱动器
                    import string
                    drives = []
                    for letter in string.ascii_uppercase:
                        drive = f"{letter}:\\"
                        if os.path.exists(drive):
                            drives.append({
                                "name": drive,
                                "path": drive,
                                "type": "drive",
                                "is_dir": True
                            })
                    return jsonify({
                        "status": "success",
                        "path": "",
                        "items": drives,
                        "parent": None
                    })
                else:
                    # Unix-like: 从根目录开始
                    path = "/"

            # 验证路径存在
            if not os.path.exists(path):
                return jsonify({
                    "status": "error",
                    "message": f"路径不存在: {path}"
                }), 404

            # 验证是目录
            if not os.path.isdir(path):
                return jsonify({
                    "status": "error",
                    "message": f"不是有效的目录: {path}"
                }), 400

            # 获取目录内容
            items = []
            try:
                for entry in os.scandir(path):
                    try:
                        # 只显示目录
                        if entry.is_dir():
                            items.append({
                                "name": entry.name,
                                "path": entry.path,
                                "type": "directory",
                                "is_dir": True
                            })
                    except (PermissionError, OSError):
                        # 跳过无权限访问的目录
                        continue
            except PermissionError:
                return jsonify({
                    "status": "error",
                    "message": f"没有权限访问: {path}"
                }), 403

            # 按名称排序
            items.sort(key=lambda x: x["name"].lower())

            # 获取父目录
            parent = str(Path(path).parent) if path != Path(path).anchor else None

            return jsonify({
                "status": "success",
                "path": path,
                "items": items,
                "parent": parent
            })

        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"浏览文件系统时出错: {e!s}"
            }), 500

    @admin_bp.route("/projects/create", methods=["POST"])
    def create_project() -> tuple[Response, int] | Response:
        """Create a new project from a given path."""
        try:
            data = request.get_json() or {}
            validated = ProjectCreateRequest(**data)
            project_info = project_service.create_project(validated.project_path)
            return jsonify(
                {
                    "status": "success",
                    "message": f"项目 '{project_info['name']}' 已创建",
                    "project": project_info,
                }
            )
        except ValidationError:
            # 验证错误由全局错误处理器处理
            raise
        except FileNotFoundError as e:
            return jsonify({"status": "error", "message": str(e)}), 404
        except FileExistsError as e:
            return jsonify({"status": "error", "message": str(e)}), 409
        except Exception as e:
            return jsonify({"status": "error", "message": f"创建项目时出错: {e!s}"}), 500

    @admin_bp.route("/projects/<project_name>/edit")
    def projects_edit(project_name: str) -> str | tuple[str, int]:
        """Render the project edit page."""
        try:
            project_detail = project_service.get_project_detail(project_name)
            languages = project_service.get_available_languages()
            return render_template("projects/detail.html", project=project_detail, languages=languages)
        except ValueError as e:
            return render_template("error.html", error_code=404, error_message=str(e)), 404

    @admin_bp.route("/projects/update", methods=["POST"])
    def update_project() -> tuple[Response, int] | Response:
        """Update a project's configuration."""
        try:
            data = request.get_json() or {}
            validated = ProjectUpdateRequest(**data)
            # Remove project_name from updates as it's used to identify the project
            updates = {k: v for k, v in validated.model_dump().items() if k not in ["project_name"] and v is not None}
            project_info = project_service.update_project(validated.project_name, updates)
            return jsonify(
                {
                    "status": "success",
                    "message": f"项目 '{project_info['name']}' 已更新",
                    "project": project_info,
                }
            )
        except ValidationError:
            # 验证错误由全局错误处理器处理
            raise
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": f"更新项目时出错: {e!s}"}), 500

    @admin_bp.route("/api/active-project")
    def get_active_project() -> Response:
        """Get the currently active project."""
        active_project = agent.get_active_project()
        if active_project:
            return jsonify({"project_name": active_project.project_name, "project_path": str(active_project.project_root)})
        else:
            return jsonify({"project_name": None, "project_path": None})

    @admin_bp.route("/tools")
    def tools_list() -> str:
        """Render the tools list page."""
        tools = tool_service.get_all_tools()
        return render_template("tools/list.html", tools=tools)

    @admin_bp.route("/tools/toggle", methods=["POST"])
    def toggle_tool() -> tuple[Response, int]:
        """Toggle tool enabled/disabled."""
        try:
            data = request.get_json() or {}
            validated = ToolToggleRequest(**data)
            # validated.enabled 在 model_validator 后保证不为 None
            enabled: bool = validated.enabled if validated.enabled is not None else False
            tool_service.toggle_tool(validated.tool_name, enabled)
            return (
                jsonify({"status": "success", "message": f"工具 '{validated.tool_name}' 已{'启用' if enabled else '禁用'}"}),
                200,
            )
        except ValidationError:
            # 验证错误由全局错误处理器处理
            raise
        except NotImplementedError:
            return jsonify({"status": "error", "message": "工具切换功能尚未实现，需要修改项目配置文件"}), 501
        except Exception as e:
            return jsonify({"status": "error", "message": f"操作失败: {e!s}"}), 500

    @admin_bp.route("/tools/stats")
    def tools_stats() -> str:
        """Render the tools statistics page."""
        stats = tool_service.get_tool_statistics()
        return render_template("tools/stats.html", stats=stats)

    @admin_bp.route("/config")
    def config_overview() -> str:
        """Render the configuration overview page."""
        config_overview = config_service.get_config_overview()
        return render_template("config/overview.html", config_overview=config_overview)

    @admin_bp.route("/monitoring/logs")
    def logs_page() -> str:
        """Render the logs viewer page."""
        limit = request.args.get("limit", 100, type=int)
        logs = monitoring_service.get_logs(limit)
        return render_template("monitoring/logs.html", logs=logs, limit=limit)

    @admin_bp.route("/api/logs")
    def api_logs() -> Response:
        """Get logs as JSON for AJAX requests."""
        limit = request.args.get("limit", 100, type=int)
        logs = monitoring_service.get_logs(limit)
        return jsonify({"logs": logs})

    @admin_bp.route("/monitoring")
    def monitoring_overview() -> str:
        """Render the system monitoring overview page."""
        system_status = monitoring_service.get_system_status()
        tasks_info = monitoring_service.get_tasks_info()
        lsp_info = monitoring_service.get_lsp_info()
        return render_template("monitoring/overview.html", system_status=system_status, tasks_info=tasks_info, lsp_info=lsp_info)

    @admin_bp.route("/monitoring/lsp")
    def lsp_monitoring() -> str:
        """Render the LSP server monitoring page."""
        lsp_status = monitoring_service.get_lsp_detailed_status()
        return render_template("monitoring/lsp.html", lsp_status=lsp_status)

    @admin_bp.route("/api/lsp-status")
    def api_lsp_status() -> Response:
        """Get LSP status as JSON for AJAX requests."""
        lsp_status = monitoring_service.get_lsp_detailed_status()
        return jsonify(lsp_status)

    @admin_bp.route("/tools/execute")
    def tools_execute_list() -> str:
        """Render the tools execution list page."""
        tools = tool_executor_service.get_all_tools()
        # 按类别分组
        categorized_tools = _categorize_tools(tools)
        return render_template("tools/execute_list.html", categorized_tools=categorized_tools)

    @admin_bp.route("/tools/execute/<tool_name>")
    def tool_execute_page(tool_name: str) -> str | tuple[str, int]:
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

    # Register the blueprint with the app
    app.register_blueprint(admin_bp)
