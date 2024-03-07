from pydantic import (
    ConfigDict,
    Field,
    FieldValidationInfo,
    computed_field,
    field_validator,
)
from zxcvbn import zxcvbn

from app.core.security import get_password_hash, is_hashed_password
from app.core.types import SecurityScopes
from app.schemas.base import DefaultModel, ExcludedField


def validate_password(password: str | None, info: FieldValidationInfo) -> str | None:
    """Validate password strength and hash it.

    Args:
        password (str): The password to validate and hash.
        info (FieldValidationInfo): The field validation info.

    Raises:
        ValueError: If the password is too weak.

    Returns:
        str: The hashed password.
    """
    if password is None:
        return password

    if is_hashed_password(password):
        # Password is already hashed, it should have been validated before being stored in the database
        # so it's ok to return it
        return password

    values = info.data
    # Validate password strength using zxcvbn
    password_strength = zxcvbn(
        password, user_inputs=list(values.values()) if values else None
    )
    if password_strength["score"] < 4:
        raise ValueError(
            f"Password is too weak: {password_strength['feedback']['warning']}"
        )
    return get_password_hash(password)


class AccountBase(DefaultModel):
    username: str = Field(..., min_length=3, max_length=32)
    last_name: str
    first_name: str
    password: str

    _validate_password = field_validator("password", mode="after")(validate_password)


class AccountCreate(AccountBase):
    @computed_field  # type: ignore[misc]
    @property
    def is_active(self) -> bool:
        return False

    @computed_field  # type: ignore[misc]
    @property
    def scope(self) -> SecurityScopes:
        return SecurityScopes.USER


class AccountUpdate(AccountBase):
    username: str | None = Field(default=None, min_length=3, max_length=32)
    last_name: str | None = None
    first_name: str | None = None
    password: str | None = None
    scope: SecurityScopes | None = None
    is_active: bool | None = None


AccountUpdate()


class OwnAccountUpdate(AccountBase):
    username: str | None = Field(default=None, min_length=3, max_length=32)
    last_name: str | None = None
    first_name: str | None = None
    password: str | None = None

    model_config = ConfigDict(extra="forbid")


class Account(AccountBase):
    """This this the account model that is linked to the database and used by the API.

    Args:
        AccountBase: The base model to use.
    """

    id: int
    password: str | None = ExcludedField
    scope: SecurityScopes
    is_active: bool

    model_config = ConfigDict(from_attributes=True)