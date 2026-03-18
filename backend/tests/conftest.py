"""
Pytest configuration for the test suite.

This module sets up the test environment by:
1. Setting DEPLOYMENT_TYPE to 'test' so the test_config.yaml is loaded
2. Clearing any cached config services to ensure fresh config loading
3. Providing common fixtures for tests
4. Providing database fixtures for release/integration tests
"""

import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Set deployment type to test before any imports that might load config
os.environ["DEPLOYMENT_TYPE"] = "test"

from backend.api.schemas.base import Base


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """
    Session-scoped fixture that ensures the test environment is properly configured.
    This runs once at the start of the test session.
    """
    # Clear the cached config service to ensure it reloads with test config
    from backend.api.config.config_dependencies import get_config_service

    get_config_service.cache_clear()

    yield

    # Cleanup after all tests
    get_config_service.cache_clear()


@pytest.fixture
def config_service():
    """
    Fixture that provides access to the ConfigService for tests that need it.
    """
    from backend.api.config.config_dependencies import get_config_service

    return get_config_service()


# ============================================================================
# Database fixtures for release/integration tests
# Uses in-memory SQLite for fast, isolated database testing
# ============================================================================


@pytest_asyncio.fixture(scope="function")
async def async_engine():
    """
    Create an async SQLite engine for testing.
    Uses in-memory SQLite database for isolation and speed.
    Each test function gets a fresh database.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session_factory(async_engine) -> async_sessionmaker[AsyncSession]:
    """
    Create an async session factory bound to the test engine.
    """
    return async_sessionmaker(
        bind=async_engine,
        autoflush=False,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(scope="function")
async def db_session(async_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a database session for tests.
    Each test gets a fresh session with automatic cleanup.

    Usage in release tests:
        @pytest.mark.release
        async def test_something(db_session):
            # Use db_session to interact with the database
            pass
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
