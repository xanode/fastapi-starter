import logging

from app.core.config.base import Settings, SupportedEnvironments


class ConfigTest(Settings):
    ALERT_BACKEND: str = "terminal"
    LOCALE_DIR: str = "app/locales"
    ALLOWED_HOSTS: list[str] = ["*"]

    LOG_LEVEL: int = logging.DEBUG
    ENVIRONMENT: SupportedEnvironments = "test"

    """ Authentication config"""
    SECRET_KEY: str = "6a50e3ddeef70fd46da504d8d0a226db7f0b44dcdeb65b97751cf2393b33693e"

    """Base account config """
    BASE_ACCOUNT_USERNAME: str = "test"
    BASE_ACCOUNT_PASSWORD: str = "test_password*45"  # to match the password policy

    ###

    """Database config"""
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str | None = "test_db"
    POSTGRES_USER: str | None = "test_user"
    POSTGRES_PASSWORD: str | None = "test_password"

    """Github config"""
    GITHUB_USER: str = "test_github_user"
    GITHUB_TOKEN: str = "test_github_token"

    ISSUE_LABELS: str = "Backend,bug,bot"
    REPOSITORY_NAME: str = "test_repository_name"
    REPOSITORY_OWNER: str = "test_repository_owner"

    @property
    def DATABASE_URI(self) -> str:
        return "sqlite+aiosqlite:///./test_app.db"