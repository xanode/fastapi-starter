from fastapi.security import SecurityScopes

from app.core.auth import check_scopes


def test_check_scopes():
    # Test that a token with "user" scope can access an endpoint that requires "user" scope
    security_scopes = SecurityScopes(scopes=["user"])
    assert check_scopes(security_scopes, ["user"]) is True

    # Test that a token with "user" scope cannot access an endpoint that requires "moderator" scope
    security_scopes = SecurityScopes(scopes=["moderator"])
    assert check_scopes(security_scopes, ["user"]) is False

    # Test that a token with "user" scope cannot access an endpoint that requires "administrator" scope
    security_scopes = SecurityScopes(scopes=["administrator"])
    assert check_scopes(security_scopes, ["user"]) is False

    # Test that a token with "moderator" scope can access an endpoint that requires "user" scope
    security_scopes = SecurityScopes(scopes=["user"])
    assert check_scopes(security_scopes, ["moderator"]) is True

    # Test that a token with "administrator" scope can access an endpoint that requires "moderator" scope
    security_scopes = SecurityScopes(scopes=["moderator"])
    assert check_scopes(security_scopes, ["administrator"]) is True
