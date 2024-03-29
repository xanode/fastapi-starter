import logging

from app.core.config import settings
from app.core.types import SecurityScopes
from app.crud.crud_account import account as accounts
from app.dependencies import get_db
from app.models.account import Account
from app.schemas import account as account_schema

logger = logging.getLogger("app.command")


async def init_db() -> None:
    logger.info("Creating initial data")

    async with get_db.get_session() as session:
        # Create account
        await accounts.create(
            db=session,
            obj_in=account_schema.AccountCreate(
                username=settings.BASE_ACCOUNT_USERNAME,
                password=settings.BASE_ACCOUNT_PASSWORD,
                last_name="Admin",
                first_name="Admin",
            ),
        )
        logger.info("Base account created")
        # Activate account
        db_obj: Account | None = await accounts.read(db=session, id=1)  # First account to be created
        assert db_obj is not None

        updated_account = account_schema.AccountUpdate(**account_schema.Account.model_validate(db_obj).model_dump())
        updated_account.is_active = True
        updated_account.scope = SecurityScopes.ADMINISTRATOR
        await accounts.update(
            db=session,
            db_obj=db_obj,
            obj_in=updated_account,
        )
        logger.info("Base account activated")

    logger.info("Initial data created")
