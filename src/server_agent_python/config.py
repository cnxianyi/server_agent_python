"""Application configuration loaded from environment variables and .env."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings.

    Every setting is prefixed with ``APP_`` when read from the environment.
    For example, ``database_url`` is configured with ``APP_DATABASE_URL``.
    """

    model_config = SettingsConfigDict(
        env_file=(".env",),
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
        extra="ignore",
    )

    name: str = "server-agent-python"
    env: str = "local"
    log_level: str = "INFO"
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/server_agent"
    )
    redis_url: str = "redis://localhost:6379/0"
    db_pool_min_size: int = Field(default=1, ge=1)
    db_pool_max_size: int = Field(default=10, ge=1)
    db_connect_timeout: int = Field(default=3, ge=1)
    redis_connect_timeout: float = Field(default=3.0, ge=0.1)
    redis_socket_timeout: float = Field(default=3.0, ge=0.1)


@lru_cache
def get_settings() -> Settings:
    """Return one cached settings object for the process."""

    return Settings()
