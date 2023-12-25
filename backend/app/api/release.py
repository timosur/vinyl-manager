from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select

from app.deps.db import get_async_session
from app.models import Release
from app.core.logger import logger
from app.service.release.csv_import import import_deejay_de
from app.service.release.sync_discogs import sync_discogs
from app.schemas.release import ReleaseUpdate
from app.models.artist import Artist
from app.models.label import Label
from app.models.track import Track
from app.service.analyze import analyze_track_audio

router = APIRouter()


@router.get("/release")
async def list_releases(session: AsyncSession = Depends(get_async_session)):
    # Prepare the select statement
    stmt = select(Release).options(
        selectinload(Release.labels),
        selectinload(Release.artists),
        selectinload(Release.tracks),
    )

    # Execute the query asynchronously
    result = await session.execute(stmt)

    # Fetch the results
    releases = result.scalars().all()

    return releases


@router.get("/release/{id}")
async def get_release(id: str, session: AsyncSession = Depends(get_async_session)):
    # Prepare the select statement
    stmt = (
        select(Release)
        .options(
            selectinload(Release.labels),
            selectinload(Release.artists),
            selectinload(Release.tracks),
        )
        .where(Release.id == id)
    )

    # Execute the query asynchronously
    result = await session.execute(stmt)

    # Fetch the results
    release = result.scalars().first()

    return release


# update a release
@router.put("/release/{id}")
async def update_release(
    id: str,
    release_update: ReleaseUpdate,
    analysis: bool = False,
    session: AsyncSession = Depends(get_async_session),
):
    # Fetch the existing release
    stmt = (
        select(Release)
        .options(
            selectinload(Release.labels),
            selectinload(Release.artists),
            selectinload(Release.tracks),
        )
        .where(Release.id == id)
    )
    result = await session.execute(stmt)
    release = result.scalars().first()

    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    # Update Release fields
    for var, value in vars(release_update).items():
        if value is not None and var not in ["labels", "artists", "tracks"]:
            setattr(release, var, value)

    # Update related entities
    existing_artist_ids = [artist.id for artist in release.artists]
    for artist_update in release_update.artists:
        if artist_update.id:
            if artist_update.id in existing_artist_ids:
                artist = next(
                    (a for a in release.artists if a.id == artist_update.id), None
                )
                # Update artist fields
                for var, value in vars(artist_update).items():
                    if value is not None:
                        setattr(artist, var, value)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Artist ID {artist_update.id} not found in release",
                )
        else:
            # Add new artist
            new_artist = Artist(**artist_update.dict(exclude={"id"}))
            release.artists.append(new_artist)

    existing_label_ids = [label.id for label in release.labels]
    for label_update in release_update.labels:
        if label_update.id:
            if label_update.id in existing_label_ids:
                label = next(
                    (l for l in release.labels if l.id == label_update.id), None
                )
                # Update label fields
                for var, value in vars(label_update).items():
                    if value is not None:
                        setattr(label, var, value)
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Label ID {label_update.id} not found in release",
                )
        else:
            # Add new label
            new_label = Label(**label_update.dict(exclude={"id"}))
            release.labels.append(new_label)

    existing_track_ids = [track.id for track in release.tracks]
    for track_update in release_update.tracks:
        if track_update.id:
            if track_update.id in existing_track_ids:
                track = next(
                    (t for t in release.tracks if t.id == track_update.id), None
                )
                # Update track fields
                for var, value in vars(track_update).items():
                    if value is not None:
                        setattr(track, var, value)
                        
                # Analyze track if audio is present
                if hasattr(track, 'audio') and track.audio and analysis:
                    analysis_result = analyze_track_audio(track.audio)
                    track.bpm = analysis_result['detected_tempo']
                    track.key = analysis_result['camelot_key_notation']

            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Track ID {track_update.id} not found in release",
                )
        else:
            # Add new track
            new_track = Track(**track_update.dict(exclude={"id"}))
            release.tracks.append(new_track)

    # Commit changes
    session.add(release)
    await session.commit()

    return release

@router.delete("/release/{id}/track/{track_id}")
async def delete_track(id: str, track_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        # Fetch the existing track
        stmt = select(Track).where(Track.id == track_id, Track.release_id == id)
        
        result = await session.execute(stmt)
        track = result.scalars().first()
        
        if not track:
            raise HTTPException(status_code=404, detail="Track not found")
        
        # Delete track
        await session.delete(track)
        
        # Commit changes
        await session.commit()

        return {"status": "OK"}

    except Exception as e:
        # Rollback the transaction
        await session.rollback()
        # Log the exception e for debugging
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/release/{id}/artist/{artist_id}")
async def delete_artist(id: str, artist_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        # Fetch the existing artist
        stmt = select(Artist).where(Artist.id == artist_id, Artist.release_id == id)
        
        result = await session.execute(stmt)
        artist = result.scalars().first()
        
        if not artist:
            raise HTTPException(status_code=404, detail="Artist not found")
        
        # Delete artist
        await session.delete(artist)
        
        # Commit changes
        await session.commit()

        return {"status": "OK"}

    except Exception as e:
        # Rollback the transaction
        await session.rollback()
        # Log the exception e for debugging
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.delete("/release/{id}/label/{label_id}")
async def delete_label(id: str, label_id: str, session: AsyncSession = Depends(get_async_session)):
    try:
        # Fetch the existing label
        stmt = select(Label).where(Label.id == label_id, Label.release_id == id)
        
        result = await session.execute(stmt)
        label = result.scalars().first()
        
        if not label:
            raise HTTPException(status_code=404, detail="Label not found")
        
        # Delete label
        await session.delete(label)
        
        # Commit changes
        await session.commit()

        return {"status": "OK"}

    except Exception as e:
        # Rollback the transaction
        await session.rollback()
        # Log the exception e for debugging
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/release/{id}/track/empty")
async def add_new_empty_track(id: str, name: str, session: AsyncSession = Depends(get_async_session)):
    try:
        # Fetch the existing release with simplified relationship loading
        stmt = select(Release).where(Release.id == id)
        result = await session.execute(stmt)
        release = result.scalars().first()

        if not release:
            raise HTTPException(status_code=404, detail="Release not found")

        # Add new track
        new_track = Track()
        new_track.name = name
        new_track.release_id = id
        
        session.add(new_track)

        # Commit changes
        await session.commit()
        
        # Return the new track
        return new_track

    except Exception as e:
        # Rollback the transaction
        await session.rollback()
        # Log the exception e for debugging
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/release/{id}/artist/empty")
async def add_new_empty_artist(id: str, name: str, session: AsyncSession = Depends(get_async_session)):
    try:
        # Fetch the existing release with simplified relationship loading
        stmt = select(Release).where(Release.id == id)
        result = await session.execute(stmt)
        release = result.scalars().first()

        if not release:
            raise HTTPException(status_code=404, detail="Release not found")

        # Add new artist
        new_artist = Artist()
        new_artist.name = name
        new_artist.release_id = id
        
        session.add(new_artist)

        # Commit changes
        await session.commit()
        
        # Return the new artist
        return new_artist

    except Exception as e:
        # Rollback the transaction
        await session.rollback()
        # Log the exception e for debugging
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post("/release/{id}/label/empty")
async def add_new_empty_label(id: str, name: str, session: AsyncSession = Depends(get_async_session)):
    try:
        # Fetch the existing release with simplified relationship loading
        stmt = select(Release).where(Release.id == id)
        result = await session.execute(stmt)
        release = result.scalars().first()

        if not release:
            raise HTTPException(status_code=404, detail="Release not found")

        # Add new label
        new_label = Label()
        new_label.name = name
        new_label.release_id = id
        
        session.add(new_label)

        # Commit changes
        await session.commit()
        
        # Return the new label
        return new_label

    except Exception as e:
        # Rollback the transaction
        await session.rollback()
        # Log the exception e for debugging
        logger.exception(e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
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
        release_ids = await import_deejay_de(session, file)

        return {"status": "OK", "created_releases": release_ids}

    except Exception as e:
        logger.exception(e)
        return {"status": "ERROR", "message": str(e)}


@router.post("/release/sync-discogs")
async def sync_discogs_collection(
    session: AsyncSession = Depends(get_async_session), username: str = ""
):
    if not username:
        raise HTTPException(status_code=422, detail="Invalid username")

    try:
        await sync_discogs(session, username)

        return {"status": "OK"}

    except Exception as e:
        logger.exception(e)
        return {"status": "ERROR", "message": str(e)}
