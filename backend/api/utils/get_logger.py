import os
from pathlib import Path

from backend.api.config.config_dependencies import get_config_service
from backend.api.config.config_service import ConfigService
from backend.api.config.models import (
    LoggingConfig,
    LoggingFileConfig,
    LoggingHandlerType,
)

from logging import Logger, getLogger, StreamHandler, Formatter
from logging.handlers import RotatingFileHandler


def get_logger(name: str) -> Logger:
    """
    Get a configured logger instance based on the application configuration.

    :param name: The name of the logger (usually __name__ of the module)

    :return: Configured Logger instance
    """
    config_service: ConfigService = get_config_service()

    logging_config: LoggingConfig = config_service.config.logging

    logger = getLogger(name)
    logger.setLevel(logging_config.level.value)

    formatter = Formatter(logging_config.format, logging_config.date_format)

    if LoggingHandlerType.CONSOLE in logging_config.handlers:
        console_handler = StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if (
        LoggingHandlerType.FILE in logging_config.handlers
        and logging_config.file.enabled
    ):
        file_config: LoggingFileConfig = logging_config.file
        file_handler = RotatingFileHandler(
            filename=file_config.filename,
            maxBytes=file_config.max_bytes,
            backupCount=file_config.backup_count,
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
