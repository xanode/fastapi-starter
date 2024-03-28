import pytest

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError

from app.core.exception_handlers import integrity_error_handler
from app.middlewares.i18n import I18nMiddleware


@pytest.mark.asyncio
async def test_integrity_error_handler():
    # Define a FastAPI app with the exception handler
    app = FastAPI()
    app.add_middleware(I18nMiddleware)
    app.add_exception_handler(IntegrityError, integrity_error_handler)

    # Define a test client for the app
    client = TestClient(app)

    # Define a test route that raises an IntegrityError
    @app.get("/test")
    async def test_route():
        raise IntegrityError(None, None, None)
    
    # Make a request to the test route to trigger the exception handler
    response = client.get("/test")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": "Relational integrity error"}