"""Project management business logic"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


class ProjectService:
    """
    Service class for managing projects in the admin dashboard.
    """

    def __init__(self, agent: "SerenaAgent") -> None:
        """
        Initialize the ProjectService.

        Args:
            agent: The SerenaAgent instance

        """
        self._agent = agent

    def get_all_projects(self) -> list[dict[str, Any]]:
        """
        Get all registered projects with their details.

        Returns:
            A list of dictionaries containing project information including:
            - name: Project name
            - path: Project root path
            - languages: List of programming languages used
            - is_active: Whether the project is currently active
            - read_only: Whether the project is in read-only mode

        """
        projects = []
        active_project = self._agent.get_active_project()

        for proj in self._agent.serena_config.projects:
            is_active = active_project and active_project.project_name == proj.project_name

            # Get languages
            languages = [lang.value for lang in proj.project_config.languages]

            projects.append(
                {
                    "name": proj.project_name,
                    "path": str(proj.project_root),
                    "languages": languages,
                    "is_active": is_active,
                    "read_only": proj.project_config.read_only,
                }
            )

        return projects

    def activate_project(self, project_name: str) -> None:
        """
        Activate a project by name.

        Args:
            project_name: The name of the project to activate

        Raises:
            ValueError: If the project is not found

        """
        self._agent.activate_project_from_path_or_name(project_name)

    def delete_project(self, project_name: str) -> None:
        """
        Delete a project by name.

        Args:
            project_name: The name of the project to delete

        Raises:
            ValueError: If the project is not found

        """
        config = self._agent.serena_config
        config.remove_project(project_name)
