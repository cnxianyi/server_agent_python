"""Loguru 日志配置。 / Loguru setup."""

import sys

from loguru import logger

from .config import Settings


def configure_logging(settings: Settings) -> None:
    """配置适用于本地和容器运行的简洁 stderr 日志。
    / Configure a concise stderr logger for local and container execution.
    """
    logger.remove()
    logger.add(
        sys.stderr,
        level=settings.log_level.upper(),
        enqueue=True,
        backtrace=False,
        diagnose=False,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | {message}"
        ),
    )
