from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from app.deps.db import get_async_session
from app.models import Release
from app.core.logger import logger
from app.service.release.csv_import import import_deejay_de

router = APIRouter()


@router.get("/release")
async def list_releases(session: AsyncSession = Depends(get_async_session)):
    # Prepare the select statement
    stmt = select(Release).options(
        joinedload(Release.label),
        joinedload(Release.artist),
        selectinload(Release.tracks),
    )

    # Execute the query asynchronously
    result = await session.execute(stmt)

    # Fetch the results
    releases = result.scalars().all()

    return releases


@router.delete("/release")
async def delete_all_releases(session: AsyncSession = Depends(get_async_session)):
    # Prepare the select statement
    stmt = select(Release)

    # Execute the query asynchronously
    result = await session.execute(stmt)

    # Fetch the results
    releases = result.scalars().all()

    # Delete all releases
    for release in releases:
        await session.delete(release)

    await session.commit()

    return releases


@router.post("/release/import-deejay-de-csv")
async def import_deejay_de_csv(
    file: UploadFile, session: AsyncSession = Depends(get_async_session)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Invalid file format")

    try:
        release_ids = import_deejay_de(session, file)

        return {"status": "OK", "created_releases": release_ids}

    except Exception as e:
        logger.exception(e)
        return {"status": "ERROR", "message": str(e)}
