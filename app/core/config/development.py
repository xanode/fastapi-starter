import logging
import os

from pydantic import Field
from typing import ClassVar

from app.core.config.base import Settings, SupportedEnvironments


class ConfigDevelopment(Settings):
    ALERT_BACKEND: str = "terminal"

    LOCALE_DIR: str = "app/locales"

    ALLOWED_HOSTS: list[str] = ["*"]

    LOG_LEVEL: int = logging.DEBUG
    ENVIRONMENT: SupportedEnvironments = "development"

    """ Authentication config"""
    # openssl rand -hex 32
    SECRET_KEY: str = Field(
        default="6a50e3ddeef70fd46da504d8d0a226db7f0b44dcdeb65b97751cf2393b33693e",
    )

    """Base account config """

    BASE_ACCOUNT_USERNAME: str = "admin"
    BASE_ACCOUNT_PASSWORD: str = "admin-password*45"

    """Database config"""

    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "fdpsql"
    POSTGRES_USER: str = "ubuntoutou"
    POSTGRES_PASSWORD: str = "totofaitdelamoto"

    """Github config"""

    GITHUB_USER: str = "test_github_user"
    GITHUB_TOKEN: str = "test_github_token"

    ISSUE_LABELS: str = "Backend,bug,bot"
    REPOSITORY_NAME: str = "test_repository_name"
    REPOSITORY_OWNER: str = "test_repository_owner"

    POSTGRES_DATABASE_URI: ClassVar[str] = (
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    SQLITE_DATABASE_URI: ClassVar[str] = "sqlite+aiosqlite:///./app.db"

    # you can change it to either SQLITE_DATABASE_URI or POSTGRES_DATABASE_URI
    @property
    def DATABASE_URI(self) -> str:
        value = os.environ.get("DB_TYPE")
        if value == "POSTGRES":
            return self.POSTGRES_DATABASE_URI

        return self.SQLITE_DATABASE_URI