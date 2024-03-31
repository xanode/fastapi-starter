import logging
import os

from functools import lru_cache

from app.core.config.base import SupportedEnvironments, SupportedLocales
from app.core.config.development import ConfigDevelopment
from app.core.config.production import ConfigProduction
from app.core.config.test import ConfigTest


logger = logging.getLogger("app.core.config")



@lru_cache
def select_settings(_env: str | None = os.getenv("ENVIRONMENT")):
    """
    Returns the application settings based on the environment specified.

    Args:
        _env (Optional[str], optional): Environment to get the settings for. Defaults to env.

    Raises:
        ValueError: If an invalid environment is specified.

    Returns:
        Settings: The application settings.
    """
    logger.info(f"Loading settings for environment {_env}")
    if _env == "development":
        return ConfigDevelopment()

    if _env == "production":
        return ConfigProduction()  # type: ignore

    if _env == "test":
        return ConfigTest()

    raise ValueError(f"Invalid environment {_env}")

settings = select_settings()