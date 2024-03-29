import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.security import create_access_token, verify_password
from app.crud.crud_account import account as accounts
from app.dependencies import CurrentAccountDependency, DBDependency, TranslationDependency
from app.schemas import account as account_schema
from app.schemas import token as token_schema

router = APIRouter(tags=["auth"], prefix="/auth")

logger = logging.getLogger("app.api.auth")

AuthFormData = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/login/", response_model=token_schema.Token)
async def login(form_data: AuthFormData, db: DBDependency, _: TranslationDependency) -> Any:
    """
    Logs in a user and returns an access token.
    """
    account = ((await accounts.query(db, username=form_data.username, limit=1))[0:1] or [None])[0]
    # Check if account exists, if password is correct and if account is active
    if account is None or not verify_password(form_data.password, account.password) or account.is_active is False:
        if account is None:
            logger.debug(f"Account {form_data.username} not found")
        elif not verify_password(form_data.password, account.password):
            logger.debug(f"Invalid password for {form_data.username}")
        elif account.is_active is False:
            logger.debug(f"Account {form_data.username} is not active")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=_("INVALID_CREDENTIALS"),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(subject=account.id, scopes=[account.scope.value])}


@router.get("/me/", response_model=account_schema.Account)
async def read_account_me(
    current_account: CurrentAccountDependency,
) -> Any:
    """
    Returns the current user's account information.
    """
    return current_account


@router.put("/me/", response_model=account_schema.Account)
async def update_account_me(
    account_in: account_schema.OwnAccountUpdate,
    current_account: CurrentAccountDependency,
    db: DBDependency,
    _: TranslationDependency,
) -> Any:
    """
    Updates the current user's account information.
    """
    # Check if username is already taken
    if account_in.username and account_in.username != current_account.username:
        if await accounts.query(db, username=account_in.username):
            logger.debug(f"Username {account_in.username} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=_("UNAVAILABLE_USERNAME"),
            )
    return await accounts.update(db, db_obj=current_account, obj_in=account_in)  # type: ignore
