"""Admin route definitions"""

from typing import TYPE_CHECKING

from flask import Blueprint, Flask, Response, jsonify, render_template, request

from serena.admin.services import get_project_service, get_tool_service

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
    project_service = get_project_service(agent)
    tool_service = get_tool_service(agent)

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

    # Register the blueprint with the app
    app.register_blueprint(admin_bp)
