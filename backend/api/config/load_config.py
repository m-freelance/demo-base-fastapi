import logging
import os
import re

import yaml
from pydantic import ValidationError

from backend.api.utils.get_deployment_type import DeploymentType, get_deployment_type

from .models import ApplicationConfig

_BASE_CONFIG_PATHS = "resources/default_config.yaml;resources/local_config.yaml"
_TEST_CONFIG_PATHS = "resources/default_config.yaml;resources/test_config.yaml"


def deep_merge(base_dict: dict, update_dict: dict) -> dict:
    """
    Recursively merge update_dict into base_dict.
    Values in update_dict will override values in base_dict, but nested dicts are merged recursively.
    This allows updating only specific fields without replacing entire nested objects.

    :param base_dict: The base dictionary
    :param update_dict: The dictionary with updates
    :return: The merged dictionary
    """
    result = base_dict.copy()
    for key, value in update_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def replace_env_variables(data, env_getter=os.getenv):
    """
    Recursively replace environment variable placeholders in the format ${VAR_NAME}
    with their actual values from the environment.

    :param data: The data structure to process (dict, list, string, or scalar)
    :param env_getter: Function to get environment variables (default: os.getenv), injectable for testing
    :return: The processed data with environment variables replaced
    """
    if isinstance(data, dict):
        return {
            key: replace_env_variables(value, env_getter) for key, value in data.items()
        }
    elif isinstance(data, list):
        return [replace_env_variables(item, env_getter) for item in data]
    elif isinstance(data, str):

        def replace_var(match):
            var_name = match.group(1)
            env_value = env_getter(var_name)
            if env_value is None:
                logger.warning(
                    f"Environment variable '{var_name}' not found, keeping placeholder"
                )
                return match.group(0)
            return env_value

        return re.sub(r"\$\{([^}]+)}", replace_var, data)
    else:
        return data


def parse_config(config_data: dict) -> ApplicationConfig:
    """
    Parse and validate configuration data into an ApplicationConfig instance.

    :param config_data: Dictionary containing configuration data
    :return: Validated ApplicationConfig instance
    :raises ValueError: If configuration validation fails
    """
    try:
        return ApplicationConfig(**config_data)
    except ValidationError as e:
        error_messages = []
        for error in e.errors():
            field_path = " -> ".join(str(x) for x in error["loc"])
            error_type = error["type"]
            error_msg = error["msg"]
            error_messages.append(
                f"Field '{field_path}': {error_msg} (type: {error_type})"
            )

        detailed_errors = "\n".join(error_messages)
        logger.error(f"configuration validation error:\n{detailed_errors}")
        raise ValueError(f"Invalid configuration:\n{detailed_errors}")


def load_yaml_file(path: str) -> dict | None:
    """
    Load and parse a YAML file.

    :param path: Path to the YAML file
    :return: Parsed YAML data as dict, or None if file doesn't exist or is empty
    """
    if not os.path.exists(path):
        logger.warning(f"configuration file {path} does not exist, skipping")
        return None

    with open(path, "r") as f:
        yaml_data = yaml.safe_load(f)
        if not yaml_data:
            logger.warning(f"configuration file {path} is empty, skipping")
            return None
        return yaml_data


def load_and_merge_configs(config_paths: list[str]) -> dict:
    """
    Load multiple YAML config files and merge them together.
    Later files override earlier ones, with nested dicts merged recursively.

    :param config_paths: List of paths to config files
    :return: Merged configuration dictionary
    """
    config_data: dict[str, object] = {}
    for path in config_paths:
        logger.info(f"loading configuration from {path}")
        yaml_data = load_yaml_file(path)
        if yaml_data:
            config_data = deep_merge(config_data, yaml_data)
    return config_data


def get_config_paths_for_deployment(deployment_type: DeploymentType) -> list[str]:
    """
    Get the list of config file paths based on deployment type.

    :param deployment_type: The deployment type
    :return: List of config file paths
    :raises ValueError: If CONFIG_PATHS env var is not set for non-local/test deployments
    """
    if deployment_type == DeploymentType.LOCAL:
        config_paths = _BASE_CONFIG_PATHS.split(";")
        logger.info(
            f"provided deployment type is local, loading configuration from default paths: %s",
            [os.path.abspath(path) for path in config_paths],
        )
    elif deployment_type == DeploymentType.TEST:
        config_paths = _TEST_CONFIG_PATHS.split(";")
        logger.info(
            f"provided deployment type is test, loading configuration from test paths: %s",
            [os.path.abspath(path) for path in config_paths],
        )
    else:
        logger.info(
            f"provided deployment type is {deployment_type.value}, loading configuration from environment variable CONFIG_PATHS"
        )
        config_paths_env = os.getenv("CONFIG_PATHS")
        if not config_paths_env:
            raise ValueError(
                "CONFIG_PATHS environment variable is not set for non-local deployment"
            )
        config_paths = config_paths_env.split(";")

    return config_paths


def get_config_from_files() -> ApplicationConfig:
    """
    Load the application configuration from files based on the deployment type.

    :return: ApplicationConfig instance
    """
    deployment_type = get_deployment_type()
    config_paths = get_config_paths_for_deployment(deployment_type)
    config_data = load_and_merge_configs(config_paths)
    config_data = replace_env_variables(config_data)
    return parse_config(config_data)


def _get_config_logger() -> logging.Logger:
    """
    Setup a logger for the configuration loading process.

    :return: Logger instance
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


# to avoid circular import, we define a simple logger here for the configuration loading process, instead of
# using the get_logger function which also depends on the configuration.
logger = _get_config_logger()
