"""Main module of the API."""

import logging
from contextlib import asynccontextmanager
import sentry_sdk
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.routing import APIRoute
from sqlalchemy.exc import IntegrityError

from app.api.api import api_router
from app.api.utils.endpoints import utils_router
from app.core.config import settings
from app.core.exception_handlers import integrity_error_handler
from app.middlewares.i18n import I18nMiddleware
from app.db.pre_start import pre_start
from app.dependencies import get_db
from app.schemas.base import HTTPError
from app.utils.custom_openapi import generate_custom_openapi
from app.utils.get_version import get_version
from app.utils.logger import setup_logs


setup_logs("app", level=logging.DEBUG)
setup_logs("uvicorn.access")
setup_logs("sqlalchemy", level=logging.WARNING)


logger = logging.getLogger("app.main")


sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
)


def custom_generate_unique_id(route: APIRoute) -> str:
    """
    Generate a unique id for each request, using the route name.
    Prefix with the version of the API if the route is deprecated.
    """
    route_name = route.name
    if route.deprecated:
        route_version = route.path.split("/")[2]
        route_name = f"{route_version}_{route_name}"
    return route_name


@asynccontextmanager
async def lifespan(_app: FastAPI):  # pragma: no cover
    """
    Context manager to run startup and shutdown events.
    """
    logger.info("Initializing database connection...")
    get_db.setup()
    await pre_start()
    logger.info("Database connection established.")
    yield
    logger.info("Closing database connection...")
    await get_db.shutdown()
    logger.info("Database connection closed.")


responses: Dict[int | str, Dict[str, Any]] | None = None


responses = {
    400: {"description": "Bad request", "model": HTTPError},
    401: {"description": "Unauthorized", "model": HTTPError},
    404: {"description": "Not found", "model": HTTPError},
    500: {
        "description": "Internal server error",
        "content": {"text/plain": {"example": "Internal server error"}},
    },
}


app = FastAPI(
    title="FastAPI-Starter API",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    version=get_version(),
    lifespan=lifespan,
    responses=responses,
    generate_unique_id_function=custom_generate_unique_id,
)

app.add_middleware(I18nMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(IntegrityError, integrity_error_handler)

app.include_router(utils_router, prefix=settings.API_PREFIX)
app.include_router(api_router, prefix=settings.API_PREFIX)

app.openapi = generate_custom_openapi(app)
