from __future__ import annotations

from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.api.db.db_exceptions import (
    DatabaseConnectionError,
    DatabaseTransactionError,
)


@dataclass(frozen=True)
class AsyncDBClient:
    engine: AsyncEngine
    SessionLocal: async_sessionmaker[AsyncSession]

    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        echo: bool = False,
        pool_pre_ping: bool = True,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> AsyncDBClient:
        """
        create an AsyncDBClient instance from a database URL. This method sets up the
        async engine and session factory with the provided configuration.

        :param url: Database connection URL (e.g., "postgresql+asyncpg://user:password@host/dbname")
        :param echo: If True, the engine will log all SQL statements. Default is False.
        :param pool_pre_ping: If True, the engine will check connections for liveness before using them. Default is True.
        :param pool_size: The size of the connection pool to maintain. Default is 5.
        :param max_overflow: The maximum number of connections to allow in connection pool "overflow", that is connections that can be opened above and beyond the pool_size setting. Default is 10.

        :return: An instance of AsyncDBClient with the configured engine and session factory.
        """
        try:
            engine = create_async_engine(
                url,
                echo=echo,
                pool_pre_ping=pool_pre_ping,
                pool_size=pool_size,
                max_overflow=max_overflow,
            )
            SessionLocal = async_sessionmaker(
                bind=engine,
                autoflush=False,
                expire_on_commit=False,
            )
            return cls(engine=engine, SessionLocal=SessionLocal)
        except SQLAlchemyError as e:
            raise DatabaseConnectionError(
                detail=f"Failed to create database engine: {str(e)}"
            ) from e
        except Exception as e:
            raise DatabaseConnectionError(
                detail=f"Unexpected error while setting up database: {str(e)}"
            ) from e

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Provide a transactional scope around a series of operations using an async session.
        This method is designed to be used as an async context manager, ensuring that
        sessions are properly committed or rolled back in case of errors.

        Usage example:
        async with db_client.session() as session:
            # perform database operations with the session

        :return: An async iterator that yields an AsyncSession instance for performing database operations.
        """
        async with self.SessionLocal() as db:
            try:
                async with db.begin():  # auto commit/rollback
                    yield db
            except SQLAlchemyError as e:
                raise DatabaseTransactionError(
                    detail=f"Database transaction failed: {str(e)}"
                ) from e
