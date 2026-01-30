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

    def create_project(self, project_path: str) -> dict[str, Any]:
        """
        Create a new project from a given path.

        Args:
            project_path: The path to the project to add

        Returns:
            A dictionary containing the created project information

        Raises:
            FileNotFoundError: If the path does not exist or is not a directory
            FileExistsError: If a project already exists at the path

        """
        from pathlib import Path

        config = self._agent.serena_config

        # Add project from path
        project_path_obj = Path(project_path).resolve()
        new_project = config.add_project_from_path(project_path_obj)

        # Return project info
        return {
            "name": new_project.project_name,
            "path": str(new_project.project_root),
            "languages": [lang.value for lang in new_project.project_config.languages],
            "is_active": True,
            "read_only": new_project.project_config.read_only,
        }

    def get_available_languages(self) -> list[str]:
        """
        Get list of available programming languages supported by Serena.

        Returns:
            A list of language names

        """
        from serena.config.ls_config import Language

        return [lang.value for lang in Language]

    def get_project_detail(self, project_name: str) -> dict[str, Any]:
        """
        Get detailed information about a specific project.

        Args:
            project_name: The name of the project

        Returns:
            A dictionary containing detailed project information

        Raises:
            ValueError: If the project is not found

        """
        config = self._agent.serena_config

        # Find the project by name
        project = None
        for proj in config.projects:
            if proj.project_config.project_name == project_name:
                project = proj
                break

        if project is None:
            raise ValueError(f"Project '{project_name}' not found")

        return {
            "name": project.project_config.project_name,
            "path": str(project.project_root),
            "languages": [lang.value for lang in project.project_config.languages],
            "ignored_paths": project.project_config.ignored_paths,
            "read_only": project.project_config.read_only,
            "ignore_all_files_in_gitignore": project.project_config.ignore_all_files_in_gitignore,
            "initial_prompt": project.project_config.initial_prompt,
            "encoding": project.project_config.encoding,
            "excluded_tools": list(project.project_config.excluded_tools) if project.project_config.excluded_tools else [],
            "fixed_tools": list(project.project_config.fixed_tools) if project.project_config.fixed_tools else [],
            "included_optional_tools": (
                list(project.project_config.included_optional_tools) if project.project_config.included_optional_tools else []
            ),
            "base_modes": list(project.project_config.base_modes) if project.project_config.base_modes else [],
            "default_modes": list(project.project_config.default_modes) if project.project_config.default_modes else [],
        }

    def update_project(self, project_name: str, updates: dict[str, Any]) -> dict[str, Any]:
        """
        Update a project's configuration.

        Args:
            project_name: The name of the project to update
            updates: A dictionary containing the fields to update

        Returns:
            A dictionary containing the updated project information

        Raises:
            ValueError: If the project is not found or validation fails

        """
        from serena.config.ls_config import Language
        from serena.config.serena_config import RegisteredProject

        config = self._agent.serena_config

        # Find the project by name
        project = None
        project_index = -1
        for i, proj in enumerate(config.projects):
            if proj.project_config.project_name == project_name:
                project = proj
                project_index = i
                break

        if project is None:
            raise ValueError(f"Project '{project_name}' not found")

        # Get the current project config
        project_config = project.project_config

        # Update fields
        if "languages" in updates:
            languages = []
            for lang_str in updates["languages"]:
                try:
                    language = Language(lang_str)
                    languages.append(language)
                except ValueError as e:
                    raise ValueError(f"Invalid language: {lang_str}") from e
            project_config.languages = languages

        if "ignored_paths" in updates:
            project_config.ignored_paths = updates["ignored_paths"]

        if "read_only" in updates:
            project_config.read_only = updates["read_only"]

        if "ignore_all_files_in_gitignore" in updates:
            project_config.ignore_all_files_in_gitignore = updates["ignore_all_files_in_gitignore"]

        if "initial_prompt" in updates:
            project_config.initial_prompt = updates["initial_prompt"]

        if "encoding" in updates:
            project_config.encoding = updates["encoding"]

        if "excluded_tools" in updates:
            project_config.excluded_tools = updates["excluded_tools"]

        if "fixed_tools" in updates:
            project_config.fixed_tools = updates["fixed_tools"]

        if "included_optional_tools" in updates:
            project_config.included_optional_tools = updates["included_optional_tools"]

        if "base_modes" in updates:
            project_config.base_modes = updates["base_modes"]

        if "default_modes" in updates:
            project_config.default_modes = updates["default_modes"]

        # Save the updated project config
        project_config.save(project.project_root)

        # Update the registered project in config
        updated_registered_project = RegisteredProject(
            project_root=str(project.project_root),
            project_config=project_config,
        )
        config.projects[project_index] = updated_registered_project

        # Save the serena config
        config.save()

        # Return updated project info
        return self.get_project_detail(project_config.project_name)
