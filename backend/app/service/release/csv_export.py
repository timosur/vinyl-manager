import csv
import json
from io import StringIO
from typing import List, Dict, Any
import base64

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.core.logger import logger
from app.models import Release, Artist, Label, Track
from app.models.artist import Artist
from app.models.artist_release_association import ArtistReleaseAssociation
from app.models.label import Label
from app.models.label_release_association import LabelReleaseAssociation


async def export_releases_to_csv(session: AsyncSession) -> str:
  """Export all releases to CSV format"""

  # Fetch all releases with related data
  stmt = select(Release).options(
    selectinload(Release.release_artists).selectinload(ArtistReleaseAssociation.artist),
    selectinload(Release.release_labels).selectinload(LabelReleaseAssociation.label),
    selectinload(Release.tracks),
  )

  result = await session.execute(stmt)
  releases = result.scalars().unique().all()

  # Prepare CSV data
  output = StringIO()
  fieldnames = ["id_number", "name", "short", "year", "format", "genre", "styles", "notes", "thumb", "purchased_at", "created_at", "updated_at", "artists", "labels", "tracks"]

  writer = csv.DictWriter(output, fieldnames=fieldnames)
  writer.writeheader()

  for release in releases:
    # Serialize artists
    artists_data = []
    for rel in release.release_artists:
      if rel.artist:
        artists_data.append(
          {
            "name": rel.artist.name,
            "id": str(rel.artist.id),
          }
        )

    # Serialize labels
    labels_data = []
    for rel in release.release_labels:
      if rel.label:
        labels_data.append(
          {
            "name": rel.label.name,
            "id": str(rel.label.id),
          }
        )

    # Serialize tracks
    tracks_data = []
    for track in release.tracks:
      track_dict = {
        "name": track.name,
        "side": track.side,
        "length": track.length,
        "key": track.key,
        "bpm": track.bpm,
        "genre": track.genre,
        "rating": track.rating,
        "id": str(track.id),
      }
      # Handle audio data - convert to base64 if it exists
      if track.audio:
        try:
          if isinstance(track.audio, str):
            track_dict["audio"] = track.audio
          else:
            # Assume it's bytes and encode to base64
            track_dict["audio"] = base64.b64encode(track.audio).decode("utf-8")
        except Exception as e:
          logger.warning(f"Could not encode audio for track {track.id}: {e}")
          track_dict["audio"] = None
      else:
        track_dict["audio"] = None

      tracks_data.append(track_dict)

    # Write release data
    writer.writerow(
      {
        "id_number": release.id_number,
        "name": release.name,
        "short": release.short,
        "year": release.year,
        "format": release.format,
        "genre": release.genre,
        "styles": release.styles,
        "notes": release.notes,
        "thumb": release.thumb,
        "purchased_at": release.purchased_at.isoformat() if release.purchased_at and hasattr(release.purchased_at, "isoformat") else release.purchased_at,
        "created_at": release.created_at.isoformat() if release.created_at and hasattr(release.created_at, "isoformat") else release.created_at,
        "updated_at": release.updated_at.isoformat() if release.updated_at and hasattr(release.updated_at, "isoformat") else release.updated_at,
        "artists": json.dumps(artists_data) if artists_data else "",
        "labels": json.dumps(labels_data) if labels_data else "",
        "tracks": json.dumps(tracks_data) if tracks_data else "",
      }
    )

  csv_content = output.getvalue()
  output.close()

  return csv_content


async def import_releases_from_csv(session: AsyncSession, file: UploadFile) -> Dict[str, Any]:
  """Import releases from CSV format"""
  import json
  from datetime import datetime

  try:
    contents = file.file.read()

    # Increase CSV field size limit to handle large audio data (10MB)
    csv.field_size_limit(10 * 1024 * 1024)

    csv_data = csv.DictReader(StringIO(contents.decode("utf-8")))

    created_releases = []
    updated_releases = []
    errors = []

    for row_num, row in enumerate(csv_data, start=1):
      try:
        # Check if release already exists by id_number
        existing_release = None
        if row.get("id_number"):
          stmt = select(Release).where(Release.id_number == row["id_number"])
          result = await session.execute(stmt)
          existing_release = result.scalar_one_or_none()

        if existing_release:
          # Update existing release
          release = existing_release
          operation = "updated"
        else:
          # Create new release
          release = Release()
          operation = "created"

        # Update release fields
        release.id_number = row.get("id_number") or release.id_number
        release.name = row.get("name") or release.name
        release.short = row.get("short") or release.short
        release.year = row.get("year") or release.year
        release.format = row.get("format") or release.format
        release.genre = row.get("genre") or release.genre
        release.styles = row.get("styles") or release.styles
        release.notes = row.get("notes") or release.notes
        release.thumb = row.get("thumb") or release.thumb

        # Handle date parsing
        if row.get("purchased_at") and row["purchased_at"].strip():
          try:
            release.purchased_at = datetime.fromisoformat(row["purchased_at"])
          except ValueError:
            pass

        if operation == "created":
          session.add(release)
          await session.flush()  # Get the ID

        # Clear existing relationships for updates
        if operation == "updated":
          # Clear existing artist associations
          for rel in release.release_artists:
            await session.delete(rel)
          # Clear existing label associations
          for rel in release.release_labels:
            await session.delete(rel)
          # Clear existing tracks
          for track in release.tracks:
            await session.delete(track)
          await session.flush()

        # Handle artists
        if row.get("artists") and row["artists"].strip():
          try:
            artists_data = json.loads(row["artists"])
            if isinstance(artists_data, list):
              for artist_data in artists_data:
                if isinstance(artist_data, dict) and "name" in artist_data:
                  # Get or create artist
                  artist_stmt = select(Artist).where(Artist.name == artist_data["name"])
                  artist_result = await session.execute(artist_stmt)
                  artist = artist_result.scalar_one_or_none()

                  if not artist:
                    artist = Artist(name=artist_data["name"])
                    session.add(artist)
                    await session.flush()

                  # Create association
                  association = ArtistReleaseAssociation(artist_id=artist.id, release_id=release.id)
                  session.add(association)
          except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not parse artists data for row {row_num}: {e}")

        # Handle labels
        if row.get("labels") and row["labels"].strip():
          try:
            labels_data = json.loads(row["labels"])
            if isinstance(labels_data, list):
              for label_data in labels_data:
                if isinstance(label_data, dict) and "name" in label_data:
                  # Get or create label
                  label_stmt = select(Label).where(Label.name == label_data["name"])
                  label_result = await session.execute(label_stmt)
                  label = label_result.scalar_one_or_none()

                  if not label:
                    label = Label(name=label_data["name"])
                    session.add(label)
                    await session.flush()

                  # Create association
                  association = LabelReleaseAssociation(label_id=label.id, release_id=release.id)
                  session.add(association)
          except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not parse labels data for row {row_num}: {e}")

        # Handle tracks
        if row.get("tracks") and row["tracks"].strip():
          try:
            tracks_data = json.loads(row["tracks"])
            if isinstance(tracks_data, list):
              for track_data in tracks_data:
                if isinstance(track_data, dict) and "name" in track_data:
                  track = Track(
                    name=track_data.get("name"),
                    side=track_data.get("side"),
                    length=track_data.get("length", 0),
                    key=track_data.get("key"),
                    bpm=track_data.get("bpm", 0),
                    genre=track_data.get("genre"),
                    rating=track_data.get("rating"),
                    release_id=release.id,
                  )

                  # Handle audio data - store as base64 string if present
                  if track_data.get("audio"):
                    # Store the base64 string directly (database expects VARCHAR)
                    track.audio = track_data["audio"]

                  session.add(track)
          except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Could not parse tracks data for row {row_num}: {e}")

        if operation == "created":
          created_releases.append(release.id_number)
        else:
          updated_releases.append(release.id_number)

      except Exception as e:
        error_msg = f"Row {row_num}: {str(e)}"
        errors.append(error_msg)
        logger.error(f"Error processing row {row_num}: {e}")
        continue

    await session.commit()

    return {
      "status": "SUCCESS",
      "created_count": len(created_releases),
      "updated_count": len(updated_releases),
      "error_count": len(errors),
      "created_releases": created_releases,
      "updated_releases": updated_releases,
      "errors": errors[:10],  # Limit errors to first 10
    }

  except Exception as e:
    await session.rollback()
    raise e
