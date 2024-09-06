import logging

from pydantic import Field

from app.core.config.base import Settings, SupportedEnvironments


class ConfigProduction(Settings):
    ALERT_BACKEND: str = "terminal"

    LOCALE_DIR: str = "app/locales"

    ALLOWED_HOSTS: list[str] = ["*"]  # ! Shouldn't be set to ["*"] in production!

    LOG_LEVEL: int = logging.INFO
    ENVIRONMENT: SupportedEnvironments = "production"

    # Authentication config
    # openssl rand -hex 32
    SECRET_KEY: str = Field(...)

    # Base account config
    BASE_ACCOUNT_USERNAME: str = "admin"
    BASE_ACCOUNT_PASSWORD: str = Field(...)

    # Database config
    POSTGRES_HOST: str = Field(...)
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = Field(...)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)

    # Github config
    GITHUB_USER: str = Field(...)
    GITHUB_TOKEN: str = Field(...)

    ISSUE_LABELS: str = "Backend,bug,bot"
    REPOSITORY_NAME: str = Field(...)
    REPOSITORY_OWNER: str = Field(...)

    @property
    def DATABASE_URI(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
