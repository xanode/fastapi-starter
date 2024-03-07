from app.main import app


def test_custom_openapi():
    # Arrange
    # Act
    openapi_schema = app.openapi()

    # Assert
    assert openapi_schema["info"]["title"] == "FastAPI-Starter API"


def test_custom_openapi_cache():
    # Arrange
    # Act
    openapi_schema = app.openapi()
    openapi_schema = app.openapi()

    # Assert
    assert openapi_schema["info"]["title"] == "FastAPI-Starter API"
