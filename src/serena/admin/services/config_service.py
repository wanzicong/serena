"""Configuration management business logic"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from serena.agent import SerenaAgent


class ConfigService:
    """
    Service class for managing Serena configuration in the admin dashboard.
    """

    def __init__(self, agent: "SerenaAgent") -> None:
        """
        Initialize the ConfigService.

        Args:
            agent: The SerenaAgent instance

        """
        self._agent = agent

    def get_config_overview(self) -> str:
        """
        Get configuration overview.

        Returns:
            A string overview of the current configuration

        """
        return self._agent.get_current_config_overview()

    def save_serena_config(self, content: str) -> None:
        """
        Save serena config YAML.

        Args:
            content: The YAML content to save

        Raises:
            ValueError: If config file path is not set

        """
        config_path = self._agent.serena_config.config_file_path
        if config_path is None:
            raise ValueError("Serena config file path not set")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)
