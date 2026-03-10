from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database import get_db


async def get_session() -> AsyncSession:
    async for session in get_db():
        return session
