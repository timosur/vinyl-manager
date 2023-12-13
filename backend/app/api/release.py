from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from app.deps.db import get_async_session
from app.models.release import Release

router = APIRouter()


@router.get("/release")
async def list_releases(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Release))
    releases = result.scalars().all()

    return releases
