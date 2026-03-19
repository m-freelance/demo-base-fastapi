from __future__ import annotations

from typing import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.db import AsyncDBClient


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """
    FastAPI dependency that provides a per-request DB session.
    """
    db: AsyncDBClient = request.app.state.db

    async with db.session() as session:
        yield session
