import csv
from http.client import HTTPException
from io import StringIO
from fastapi import APIRouter, Depends, UploadFile
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select, insert

from app.deps.db import get_async_session
from app.models import Artist, Label, Release


router = APIRouter()

@router.get("/release")
async def list_releases(session: AsyncSession = Depends(get_async_session)):
    # Prepare the select statement
    stmt = (
        select(Release)
        .options(joinedload(Release.label), joinedload(Release.artist))
    )

    # Execute the query asynchronously
    result = await session.execute(stmt)

    # Fetch the results
    releases = result.scalars().all()

    return releases

@router.delete("/release")
async def delete_all_releases(session: AsyncSession = Depends(get_async_session)):
    # Prepare the select statement
    stmt = (
        select(Release)
    )

    # Execute the query asynchronously
    result = await session.execute(stmt)

    # Fetch the results
    releases = result.scalars().all()

    for release in releases:
        await session.delete(release)

    await session.commit()

    return releases

@router.post("/release/import-deejay-de-csv")
async def import_deejay_de_csv(file: UploadFile, session: AsyncSession = Depends(get_async_session)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=422, detail="Invalid file format")
    
    try:
        # Read CSV from request body
        contents = file.file.read()
        buffer = StringIO(contents.decode('utf-8'))
        csv_rows = csv.DictReader(buffer, delimiter=';')
        csv_data = [row for row in csv_rows]

        release_ids = []
        for item in csv_data:
            if all(key in item for key in ['Artist', 'Title', 'Label', 'Label No']):
                # check if artist exists, if not create it
                artist = await session.execute(select(Artist).where(Artist.name == item['Artist']))
                artist = artist.scalars().first()
                if not artist:
                    artist_id = await session.execute(insert(Artist).values(name=item['Artist']))
                else:
                    artist_id = artist.id

                # check if label exists, if not create it
                label = await session.execute(select(Label).where(Label.name == item['Label']))
                label = label.scalars().first()
                if not label:
                    label_id = await session.execute(insert(Label).values(name=item['Label']))
                else:
                    label_id = label.id

                # check if release exists, if not create it
                release = await session.execute(select(Release).where(Release.name == item['Title']))
                release = release.scalars().first()
                if not release:
                    release_id = await session.execute(insert(Release).values(
                        name=item['Title'],
                        short=item['Label No'],
                        artist_id=artist_id,
                        label_id=label_id
                    ))
                else:
                    release_id = release.id

                release_ids.append(release_id)

        return {"status": "OK", "created": release_ids}

    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
    
