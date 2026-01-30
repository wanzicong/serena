"""Admin route definitions"""

from typing import TYPE_CHECKING

from flask import Blueprint, Flask, Response, jsonify, render_template, request

from serena.admin.services import get_config_service, get_monitoring_service, get_project_service, get_tool_service

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


def register_admin_routes(app: Flask, agent: "SerenaAgent") -> None:
    """
    Register admin routes with the Flask application.

    Args:
        app: The Flask application instance
        agent: The SerenaAgent instance

    """
    # Create a blueprint for admin routes
    admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

    # Get service instances
    config_service = get_config_service(agent)
    project_service = get_project_service(agent)
    tool_service = get_tool_service(agent)
    monitoring_service = get_monitoring_service(agent)

    @admin_bp.route("/projects")
    def projects_list() -> str:
        """Render the projects list page."""
        projects = project_service.get_all_projects()
        return render_template("projects/list.html", projects=projects)

    # Note: activate and delete routes implemented here for complete UX
    # Originally planned for Task 4, but implemented early for better user experience
    @admin_bp.route("/projects/activate", methods=["POST"])
    def activate_project() -> tuple[Response, int] | Response:
        """Activate a project by name."""
        data = request.get_json()
        project_name = data.get("project_name")

        if not project_name:
            return jsonify({"status": "error", "message": "项目名称不能为空"}), 400

        try:
            project_service.activate_project(project_name)
            return jsonify({"status": "success", "message": f"项目 '{project_name}' 已激活"})
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": f"激活项目时出错: {e!s}"}), 500

    @admin_bp.route("/projects/delete", methods=["POST"])
    def delete_project() -> tuple[Response, int] | Response:
        """Delete a project by name."""
        data = request.get_json()
        project_name = data.get("project_name")

        if not project_name:
            return jsonify({"status": "error", "message": "项目名称不能为空"}), 400

        try:
            project_service.delete_project(project_name)
            return jsonify({"status": "success", "message": f"项目 '{project_name}' 已删除"})
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 404
        except Exception as e:
            return jsonify({"status": "error", "message": f"删除项目时出错: {e!s}"}), 500

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
        data = request.get_json()
        tool_name = data.get("tool_name")
        enabled = data.get("enabled")

        if not tool_name or enabled is None:
            return jsonify({"status": "error", "message": "缺少参数"}), 400

        try:
            tool_service.toggle_tool(tool_name, enabled)
            return jsonify({"status": "success", "message": f"工具 '{tool_name}' 已{'启用' if enabled else '禁用'}"}), 200
        except NotImplementedError:
            return jsonify({"status": "error", "message": "工具切换功能尚未实现，需要修改项目配置文件"}), 501
        except Exception as e:
            return jsonify({"status": "error", "message": f"操作失败: {e!s}"}), 500

    @admin_bp.route("/config")
    def config_overview() -> str:
        """Render the configuration overview page."""
        config_overview = config_service.get_config_overview()
        return render_template("config/overview.html", config_overview=config_overview)

    @admin_bp.route("/monitoring")
    def monitoring_overview() -> str:
        """Render the system monitoring overview page."""
        system_status = monitoring_service.get_system_status()
        tasks_info = monitoring_service.get_tasks_info()
        lsp_info = monitoring_service.get_lsp_info()
        return render_template("monitoring/overview.html", system_status=system_status, tasks_info=tasks_info, lsp_info=lsp_info)

    # Register the blueprint with the app
    app.register_blueprint(admin_bp)
