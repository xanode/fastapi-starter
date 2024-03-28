from fastapi import APIRouter

from app.schemas.utils_endpoints import HealthResponse, RootResponse, VersionResponse
from app.utils.get_version import get_version


utils_router = APIRouter(tags=["utils"])


@utils_router.get("/", status_code=200, response_model=RootResponse)
async def root():
    """
    Root endpoint.
    """
    return {"msg": "Hello, World!"}


@utils_router.get("/health", status_code=200, response_model=HealthResponse)
async def health():
    """
    Health endpoint.
    """
    return {"status": "Ok"}


@utils_router.get("/version", status_code=200, response_model=VersionResponse)
async def version():
    """
    Version endpoint.
    """
    return {"version": get_version()}
