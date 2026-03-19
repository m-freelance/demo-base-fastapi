from functools import lru_cache

from backend.api.config.config_service import ConfigService


@lru_cache()
def get_config_service():
    """
    FastAPI dependency that provides a singleton ConfigService instance.

    :return: a ConfigService instance that can be used across the entire application to access configuration settings loaded from environment variables and .env files.
    """
    return ConfigService()
