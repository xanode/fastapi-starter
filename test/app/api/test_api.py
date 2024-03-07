from fastapi import APIRouter

from app.api.api import api_router
from app.api.endpoints.account import router as account_router
from app.api.endpoints.auth import router as auth_router


def test_api_router():
    assert isinstance(api_router, APIRouter)


def test_api_router_include_all_router():
    all_routers = [
        account_router,
        auth_router,
    ]
    for router in all_routers:
        for route in router.routes:
            assert route in api_router.routes
