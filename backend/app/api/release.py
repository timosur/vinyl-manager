from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.logger import logger
from app.deps.db import get_async_session
from app.models import Release
from app.models.artist import Artist
from app.models.artist_release_association import ArtistReleaseAssociation
from app.models.label import Label
from app.models.label_release_association import LabelReleaseAssociation
from app.models.track import Track
from app.schemas.release import ReleaseUpdate
from app.service.analyze import analyze_track_audio
from app.service.release.csv_import import import_deejay_de
from app.service.release.sync_discogs import sync_discogs

router = APIRouter()


@router.get("/release")
async def list_releases(session: AsyncSession = Depends(get_async_session), pageLimit: int = 20, page: int = 1, sortColumn: str = "id_number", sortOrder: str = "asc", searchTerm: str = ""):
  # Prepare the select statement
  stmt = (
    select(Release)
    .options(
      joinedload(Release.release_artists).joinedload(ArtistReleaseAssociation.artist),
      joinedload(Release.release_labels).joinedload(LabelReleaseAssociation.label),
      selectinload(Release.tracks).load_only(Track.id, Track.name, Track.genre, Track.bpm, Track.key, Track.rating, Track.side),
    )
    .order_by(Release.id_number.asc())
  )

  # Execute the query asynchronously
  result = await session.execute(stmt)

  # Fetch the results
  releases = result.unique().scalars().all()

  # Map labels and artists to release
  for release in releases:
    release.labels = [assoc.label for assoc in release.release_labels]
    release.artists = [assoc.artist for assoc in release.release_artists]

    # Remove association objects
    del release.release_labels
    del release.release_artists

  # Sort releases
  if sortColumn == "id_number":
    releases = sorted(releases, key=lambda x: x.id_number if x.id_number else "999999", reverse=True if sortOrder == "desc" else False)
  elif sortColumn == "name":
    releases = sorted(releases, key=lambda x: x.name, reverse=True if sortOrder == "desc" else False)
  elif sortColumn == "artists":
    releases = sorted(releases, key=lambda x: ", ".join([artist.name for artist in x.artists]), reverse=True if sortOrder == "desc" else False)
  elif sortColumn == "labels":
    releases = sorted(releases, key=lambda x: ", ".join([label.name for label in x.labels]), reverse=True if sortOrder == "desc" else False)
  elif sortColumn == "styles":
    releases = sorted(releases, key=lambda x: x.styles if x.styles else "", reverse=True if sortOrder == "desc" else False)
  elif sortColumn == "tracks":
    releases = sorted(releases, key=lambda x: len(x.tracks), reverse=True if sortOrder == "desc" else False)
  elif sortColumn == "created_at":
    releases = sorted(releases, key=lambda x: x.created_at, reverse=True if sortOrder == "desc" else False)

  # Search releases, search in name, tracks, labels, artists, genre and styles, check if the search field is not empty or none
  if searchTerm and searchTerm != "":
    releases = [release for release in releases if searchTerm.lower() in release.name.lower() or
                any([searchTerm.lower() in track.name.lower() for track in release.tracks]) or
                any([searchTerm.lower() in artist.name.lower() for artist in release.artists]) or
                any([searchTerm.lower() in label.name.lower() for label in release.labels]) or
                any([searchTerm.lower() in track.genre.lower() if track.genre else False for track in release.tracks]) or
                any([searchTerm.lower() in release.styles.lower() if release.styles else False])]
    
  # Calculate pagination
  total = len(releases)
  start = (page - 1) * pageLimit
  end = start + pageLimit if start + pageLimit < total else total
  releases = releases[start:end]
  pageCount = total / pageLimit if total % pageLimit == 0 else total // pageLimit + 1

  return {"total": total, "page": page, "maxPage": pageCount, "items": releases, "start": start + 1, "end": end}


@router.get("/release/{id}")
async def get_release(id: str, session: AsyncSession = Depends(get_async_session)):
  # Prepare the select statement
  stmt = (
    select(Release)
    .options(
      joinedload(Release.release_artists).joinedload(ArtistReleaseAssociation.artist),
      joinedload(Release.release_labels).joinedload(LabelReleaseAssociation.label),
      selectinload(Release.tracks),
    )
    .where(Release.id == id)
  )

  # Execute the query asynchronously
  result = await session.execute(stmt)

  # Fetch the results
  release = result.unique().scalars().first()

  # Get latest id_number + 1 (e.g. 000002) number is a string, int needs to be extracted first by removing leading zeros
  if release.id_number is None or release.id_number == "":
    stmt = select(Release).where(Release.id_number != None).order_by(Release.id_number.desc()).limit(1)
    result = await session.execute(stmt)
    latest_release = result.scalars().first()
    if latest_release:
      release.id_number = str(int(latest_release.id_number) + 1).zfill(6)

  # Map labels and artists to release
  release.labels = [assoc.label for assoc in release.release_labels]
  release.artists = [assoc.artist for assoc in release.release_artists]

  # Remove association objects
  del release.release_labels
  del release.release_artists

  return release


# update all release styles, combining track styles
@router.put("/release/styles")
async def update_release_styles(session: AsyncSession = Depends(get_async_session)):
  # Prepare the select statement
  stmt = select(Release).options(selectinload(Release.tracks))

  # Execute the query asynchronously
  result = await session.execute(stmt)

  # Fetch the results
  releases = result.unique().scalars().all()

  # Update styles
  for release in releases:
    styles = []
    for track in release.tracks:
      if track.genre:
        styles.append(track.genre)

    # Remove duplicate styles
    release.styles = ", ".join(list(set(styles)))

    # Commit changes
    session.add(release)

  await session.commit()

  return {"status": "OK"}


# delete a release
@router.delete("/release/{id}")
async def delete_release(id: str, session: AsyncSession = Depends(get_async_session)):
  try:
    # Fetch the existing release
    stmt = select(Release).where(Release.id == id)

    result = await session.execute(stmt)
    release = result.scalars().first()

    if not release:
      raise HTTPException(status_code=404, detail="Release not found")

    # Delete all tracks for this release
    stmt = select(Track).where(Track.release_id == id)
    result = await session.execute(stmt)
    tracks = result.scalars().all()
    for track in tracks:
      await session.delete(track)

    # Delete all artists for this release
    stmt = select(ArtistReleaseAssociation).where(ArtistReleaseAssociation.release_id == id)
    result = await session.execute(stmt)
    artist_assocs = result.scalars().all()
    for artist_assoc in artist_assocs:
      await session.delete(artist_assoc)

    # Delete all labels for this release
    stmt = select(LabelReleaseAssociation).where(LabelReleaseAssociation.release_id == id)
    result = await session.execute(stmt)
    label_assocs = result.scalars().all()
    for label_assoc in label_assocs:
      await session.delete(label_assoc)

    # Delete release
    await session.delete(release)

    # Commit changes
    await session.commit()

    return {"status": "OK"}

  except Exception as e:
    # Rollback the transaction
    await session.rollback()
    # Log the exception e for debugging
    logger.exception(e)
    raise HTTPException(status_code=500, detail="Internal Server Error")


# update a release
@router.put("/release/{id}")
async def update_release(
  id: UUID4,
  release_update: ReleaseUpdate,
  analysis: bool = False,
  session: AsyncSession = Depends(get_async_session),
):
  # Fetch the existing release along with its artists, labels, and tracks
  stmt = (
    select(Release)
    .options(
      joinedload(Release.release_artists).joinedload(ArtistReleaseAssociation.artist),
      joinedload(Release.release_labels).joinedload(LabelReleaseAssociation.label),
      joinedload(Release.tracks),
    )
    .where(Release.id == id)
  )
  result = await session.execute(stmt)
  release = result.scalars().first()

  if not release:
    raise HTTPException(status_code=404, detail="Release not found")

  # Update Release fields
  release_data = release_update.dict(exclude_unset=True)
  for key, value in release_data.items():
    if key in {"artists", "labels", "tracks"}:
      continue  # Skip relationships here
    setattr(release, key, value)

  # Update Artists
  if release_update.artists is not None:
    existing_artists = {assoc.artist_id: assoc for assoc in release.release_artists}
    for artist_update in release_update.artists:
      artist_assoc = existing_artists.get(artist_update.id)
      if artist_assoc:
        for key, value in artist_update.dict(exclude_unset=True).items():
          setattr(artist_assoc.artist, key, value)
      else:
        logger.info(f"Artist {artist_update.id} not found in release {release.id}")

  # Update Labels
  if release_update.labels is not None:
    existing_labels = {assoc.label_id: assoc for assoc in release.release_labels}
    for label_update in release_update.labels:
      label_assoc = existing_labels.get(label_update.id)
      if label_assoc:
        for key, value in label_update.dict(exclude_unset=True).items():
          setattr(label_assoc.label, key, value)
      else:
        logger.info(f"Label {label_update.id} not found in release {release.id}")

  # Update Tracks
  if release_update.tracks is not None:
    track_dict = {track.id: track for track in release.tracks}
    styles = []

    for track_update in release_update.tracks:
      track = track_dict.get(track_update.id)
      if track:
        for key, value in track_update.dict(exclude_unset=True).items():
          setattr(track, key, value)

        if track.genre:
          styles.append(track.genre)

        if analysis and track.audio:
          # Assuming analyze_track_audio is a function you have defined
          analysis_result = analyze_track_audio(track.audio)
          track.bpm = analysis_result["detected_tempo"]
          track.key = analysis_result["camelot_key_notation"]
      else:
        logger.info(f"Track {track_update.id} not found in release {release.id}")

    # Update release styles on basis of track styles
    release.styles = ", ".join(list(set(styles)))

  # Commit changes
  session.add(release)
  await session.commit()

  # Return the updated release
  # Map labels and artists to release
  release.labels = [assoc.label for assoc in release.release_labels]
  release.artists = [assoc.artist for assoc in release.release_artists]

  # Remove association objects
  del release.release_labels
  del release.release_artists

  return release


# create a empty release
@router.post("/release/empty")
async def create_empty_release(name: str, session: AsyncSession = Depends(get_async_session)):
  # Create new release
  new_release = Release(name=name)

  session.add(new_release)
  await session.commit()

  return new_release


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

    # Create new artist
    new_artist = Artist(name=name)
    session.add(new_artist)
    await session.flush()

    # Create association
    new_assoc = ArtistReleaseAssociation(artist_id=new_artist.id, release_id=id)
    session.add(new_assoc)

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
    await session.flush()

    # Create association
    new_assoc = LabelReleaseAssociation(label_id=new_label.id, release_id=id)
    session.add(new_assoc)

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
async def import_deejay_de_csv(file: UploadFile, session: AsyncSession = Depends(get_async_session)):
  if not file.filename.endswith(".csv"):
    raise HTTPException(status_code=422, detail="Invalid file format")

  try:
    release_ids = await import_deejay_de(session, file)

    return {"status": "OK", "created_releases": release_ids}

  except Exception as e:
    logger.exception(e)
    return {"status": "ERROR", "message": str(e)}


@router.post("/release/sync-discogs")
async def sync_discogs_collection(session: AsyncSession = Depends(get_async_session), username: str = ""):
  if not username:
    raise HTTPException(status_code=422, detail="Invalid username")

  try:
    await sync_discogs(session, username)

    return {"status": "OK"}

  except Exception as e:
    logger.exception(e)
    return {"status": "ERROR", "message": str(e)}
