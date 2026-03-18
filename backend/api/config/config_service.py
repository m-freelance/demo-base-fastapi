from backend.api.config.models import ApplicationConfig
from backend.api.config.load_config import get_config_from_files


class ConfigService:
    def __init__(self):
        self._config_instance: ApplicationConfig = get_config_from_files()

    @property
    def config(self) -> ApplicationConfig:
        """
        Get the application configuration instance.

        :return: ApplicationConfig instance
        """
        return self._config_instance
