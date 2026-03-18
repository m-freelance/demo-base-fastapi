from enum import Enum


class DeploymentType(Enum):
    LOCAL = "local"
    TEST = "test"
    DEVELOPMENT = "dev"
    PRODUCTION = "prod"


def get_deployment_type() -> DeploymentType:
    """
    Get the deployment type from the environment variable.

    :return: DeploymentType enum value
    """
    import os

    deployment_type_str = os.getenv("DEPLOYMENT_TYPE", "local").lower()
    try:
        return DeploymentType(deployment_type_str)
    except ValueError:
        raise ValueError(
            f"Invalid DEPLOYMENT_TYPE: {deployment_type_str}. Must be one of: {[e.value for e in DeploymentType]}"
        )
