import logging
from os import environ

from rich.logging import RichHandler


def get_logger(
    name: str,
    level: int = logging.getLevelNamesMapping().get(
        environ.get("LOG_LEVEL", "INFO"), logging.INFO
    ),
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(RichHandler())
    return logger
