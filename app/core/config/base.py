from abc import abstractmethod
from typing import Literal

from pydantic_settings import BaseSettings


SupportedLocales = Literal["en-US", "fr-FR"]
SupportedEnvironments = Literal["development", "production", "test"]


class Settings(BaseSettings):
    """
    This class defines the application settings and configurations.

    Attributes:
    -----------
    ALERT_BACKEND : str
        The alert backend to use.
    API_PREFIX : str
        The prefix for API routes.
    LOCALE : SupportedLocales
        The supported locale for the application.
    ALLOWED_HOSTS : list[str]
        The list of allowed hosts for the application.
    LOG_LEVEL : int
        The log level for the application.
    ENVIRONMENT : SupportedEnvironments
        The environment for the application.

    ACCESS_TOKEN_EXPIRE_MINUTES : int
        The expiration time for access tokens in minutes.
    SECRET_KEY : str
        The secret key for JWT authentication.
    ALGORITHM : str
        The algorithm to use for JWT authentication.

    BASE_ACCOUNT_USERNAME : str
        The username for the base account.
    BASE_ACCOUNT_PASSWORD : str
        The password for the base account.

    POSTGRES_HOST : str | None
        The host for the PostgreSQL database.
    POSTGRES_PORT : int
        The port for the PostgreSQL database.
    POSTGRES_DB : str | None
        The name of the PostgreSQL database.
    POSTGRES_USER : str | None
        The username for the PostgreSQL database.
    POSTGRES_PASSWORD : str | None
        The password for the PostgreSQL database.
    DATABASE_URI : str
        The URI for the database.

    GITHUB_USER : str
        The username for the GitHub account.
    GITHUB_TOKEN : str
        The token for the GitHub account.
    ISSUE_LABELS : str
        The labels for GitHub issues.
    REPOSITORY_NAME : str
        The name of the GitHub repository.
    REPOSITORY_OWNER : str
        The owner of the GitHub repository.
    """

    ALERT_BACKEND: str
    API_PREFIX: str = "/api"
    LOCALE_DIR: str
    DEFAULT_LOCALE: str = "en-US"
    SUPPORTED_LOCALES: list[SupportedLocales] = list(SupportedLocales.__args__)

    ALLOWED_HOSTS: list[str]

    LOG_LEVEL: int
    ENVIRONMENT: SupportedEnvironments

    # Authentication config

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1  # 1 day
    SECRET_KEY: str
    ALGORITHM: str = "HS256"  # TODO: Change to ES256 in the future

    # Base account config

    BASE_ACCOUNT_USERNAME: str
    BASE_ACCOUNT_PASSWORD: str

    # Database config

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    @property
    @abstractmethod
    def DATABASE_URI(self) -> str:
        """The URI for the database."""

    # Github config

    GITHUB_USER: str
    GITHUB_TOKEN: str
    ISSUE_LABELS: str
    REPOSITORY_NAME: str
    REPOSITORY_OWNER: str