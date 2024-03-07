from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, call, patch

from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.databases.postgres import PostgresDatabase
from unittest.mock import AsyncMock

postgres_url = URL.create(
    drivername="postgresql+asyncpg",
    username=settings.POSTGRES_USER,
    password=settings.POSTGRES_PASSWORD,
    host=settings.POSTGRES_HOST,
    port=settings.POSTGRES_PORT,
    database=settings.POSTGRES_DB,
)


class TestPostgresDatabase(IsolatedAsyncioTestCase):
    @patch("app.db.databases.postgres.async_sessionmaker")
    @patch("app.db.databases.postgres.create_async_engine")
    def test_setup(self, mock_create_async_engine, mock_async_sessionmaker):
        mock_async_engine = AsyncMock()
        mock_create_async_engine.return_value = mock_async_engine
        mock_async_sessionmaker.return_value = AsyncMock(spec=AsyncSession)

        db = PostgresDatabase()
        db.setup()

        mock_create_async_engine.assert_called_once_with(
            postgres_url,
            pool_pre_ping=True,
        )
        mock_async_sessionmaker.assert_called_once_with(
            mock_async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    @patch("app.db.databases.postgres.asyncpg.connect")
    async def test_drop(self, mock_connect):
        mock_connection = AsyncMock()
        mock_connect.return_value = mock_connection

        db = PostgresDatabase()
        await db.drop()

        mock_connect.assert_called_once_with(
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
        )
        mock_connection.execute.assert_has_calls(
            [
                call("DROP SCHEMA public CASCADE"),
                call("CREATE SCHEMA public"),
            ]
        )

    @patch("app.db.databases.postgres.PostgresDatabase.get_session")
    async def test_drop_alembic_version(self, mock_get_session):
        mock_session = AsyncMock(spec=AsyncSession)
        mock_get_session.return_value.__aenter__.return_value = mock_session

        db = PostgresDatabase()
        await db.drop_alembic_version()

        mock_get_session.assert_called_once()
        mock_session.execute.assert_awaited_once()
        actual_args, _ = mock_session.execute.await_args
        assert str(actual_args[0]) == "DROP TABLE IF EXISTS alembic_version"
        mock_session.commit.assert_awaited_once()