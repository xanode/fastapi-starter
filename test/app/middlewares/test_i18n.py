import pytest

from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import patch

from app.core.config import settings, SupportedLocales
from app.middlewares.i18n import I18nMiddleware


@pytest.mark.asyncio
@patch("app.middlewares.i18n.gettext.translation")
async def test_i18n_middleware(mock_gettext):
    # Define a FastAPI app with the middleware
    app = FastAPI()
    app.add_middleware(I18nMiddleware)

    # Define a test client for the app
    client = TestClient(app)

    # Define a test route that returns nothing
    @app.get("/")
    async def test_route():
        return {}

    for locale in settings.SUPPORTED_LOCALES:
        # Make a request with the given locale and check that the locale is set correctly
        response = client.get("/", headers={"Accept-Language": locale})
        assert response.status_code == status.HTTP_200_OK
        #assert response.request.state.translation is not None
        mock_gettext.assert_called_with('base', localedir=settings.LOCALE_DIR, languages=[locale])
    
    # Make a request with an unsupported locale and check that the default locale is used
    response = client.get("/", headers={"Accept-Language": "unsupported"})
    assert response.status_code == status.HTTP_200_OK
    #assert response.request.state.translation is not None
    mock_gettext.assert_called_with('base', localedir=settings.LOCALE_DIR, languages=[settings.DEFAULT_LOCALE])

    # Check that the middleware caches the locale and translation
    locale: SupportedLocales = settings.SUPPORTED_LOCALES[0]
    response = client.get("/", headers={"Accept-Language": locale})
    assert response.status_code == status.HTTP_200_OK
    mock_gettext.assert_called_with('base', localedir=settings.LOCALE_DIR, languages=[locale])
    mock_gettext.reset_mock()
    response = client.get("/", headers={"Accept-Language": locale})
    assert response.status_code == status.HTTP_200_OK
    mock_gettext.assert_not_called()
    