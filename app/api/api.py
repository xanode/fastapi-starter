from fastapi import APIRouter

from app.api import endpoints
from app.utils.load_submodules import load_submodules

endpoints_modules = load_submodules(endpoints)

api_router = APIRouter()


for module in endpoints_modules:
    api_router.include_router(module.router)
