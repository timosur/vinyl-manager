import csv
from io import StringIO

import requests

from app.core.logger import logger
from app.models import (
  Artist,
  ArtistReleaseAssociation,
  Label,
  LabelReleaseAssociation,
  Release,
  Track,
)
from app.service.discogs import discogs_search_release
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession


async def import_deejay_de(session: AsyncSession, file: UploadFile):
  try:
    contents = file.file.read()
    csv_data = csv.DictReader(StringIO(contents.decode("utf-8")), delimiter=";")

    release_ids = []
    for item in csv_data:
      if not all(key in item for key in ["Artist", "Title", "Label", "Label No"]):
        continue

      release = await get_release(session, item["Title"], item["Label No"])
      if release:
        logger.info(f"Skipping existing release: {item['Title']}")
        continue

      original_release = await find_discogs_release(item)
      if original_release is None:
        original_release = await create_release_from_deejay(item)

      release_id = await insert_release(session, item, original_release)
      if release_id is None:
        continue

      artist = await get_or_create_artist(session, item["Artist"])
      await associate_artist_with_release(session, artist, release_id)

      label = await get_or_create_label(session, item["Label"])
      await associate_label_with_release(session, label, release_id)

      if original_release.get("tracklist"):
        await add_tracks_to_release(session, original_release["tracklist"], release_id)

      await session.commit()
      release_ids.append(release_id)

    return release_ids

  except Exception as e:
    logger.error(f"Error importing data: {e}")
    raise


async def get_release(session: AsyncSession, title: str, catno: str):
  result = await session.execute(
    select(Release).where(Release.short == catno and Release.name == title)
  )
  return result.scalar_one_or_none()


async def find_discogs_release(item: dict):
  original_release = discogs_search_release(f"{item['Title']} {item['Label No']}")

  if original_release is None:
    logger.warning(
      f"Could not find discogs release for {item['Title']} {item['Label No']}"
    )

    # Try again without the label number
    original_release = discogs_search_release(item["Title"])

    if original_release is None:
      logger.warning(f"Could not find discogs release for {item['Title']}")

  # Check if release catno matches Label No and if label name matches label, remove all whitespace, lowercase
  if original_release is not None and (
    original_release["catno"].lower().replace(" ", "")
    != item["Label No"].lower().replace(" ", "")
    or item["Label"].lower().replace(" ", "")
    not in original_release["all_labels"].lower().replace(" ", "")
  ):
    logger.warning(
      f"Discogs release {original_release['title']} does not match deejay.de release {item['Title']}"
    )

    original_release = None

  return original_release


async def create_release_from_deejay(item: dict):
  logger.info(f"Getting tracklist from deejay.de for {item['Title']}")

  # Call https://www.deejay.de/ajaxHelper/fp.php?t=item["ID"]&DEEJAY_SHOP=&s=
  # Get tracklist from response
  request_url = (
    f"https://www.deejay.de/ajaxHelper/fp.php?t={item['ID']}&DEEJAY_SHOP=&s="
  )
  response = requests.get(request_url)
  release_info = response.text

  # Splitting the string into parts
  parts = release_info.split("~")

  # Identifying parts with track information
  # Assuming that track info parts contain '\', followed by a side and track number (e.g., A1, B2)
  track_info_parts = [part for part in parts if "\\" in part and "|" in part]

  # Extracting track names and sides
  tracks = []
  for part in track_info_parts:
    side_track_split = part.split("\\")[-1].split(
      "|"
    )  # Splitting to get side and track number
    side_and_track_number = side_track_split[
      0
    ].strip()  # Extracting the side and track number (e.g., A1, B2)
    track_name = side_track_split[1].strip()  # Extracting the track name
    tracks.append(
      {
        "title": track_name,
        "position": side_and_track_number,
        "duration": None,
      }
    )

  return {
    "catno": item["Label No"],
    "thumb": None,
    "year": None,
    "genres": "Electronic",
    "styles": None,
    "format": "Vinyl",
    "tracklist": tracks,
  }


async def insert_release(session: AsyncSession, item: dict, original_release: dict):
  release = Release(
    name=item["Title"],
    short=item["Label No"],
    thumb=original_release["thumb"],
    year=original_release["year"],
    genre=original_release["genres"],
    styles=original_release["styles"],
    format=original_release["format"],
  )

  session.add(release)
  await session.flush()

  return release.id


async def get_or_create_artist(session: AsyncSession, name: str):
  artist = await session.execute(select(Artist).where(Artist.name == name))
  artist = artist.scalar_one_or_none()

  if artist is None:
    artist = Artist(name=name)
    session.add(artist)
    await session.flush()

  return artist


async def associate_artist_with_release(
  session: AsyncSession, artist: Artist, release_id: int
):
  association = ArtistReleaseAssociation(artist_id=artist.id, release_id=release_id)
  session.add(association)


async def get_or_create_label(session: AsyncSession, name: str):
  label = await session.execute(select(Label).where(Label.name == name))
  label = label.scalar_one_or_none()

  if label is None:
    label = Label(name=name)
    session.add(label)
    await session.flush()

  return label


async def associate_label_with_release(
  session: AsyncSession, label: Label, release_id: int
):
  association = LabelReleaseAssociation(label_id=label.id, release_id=release_id)
  session.add(association)


async def add_tracks_to_release(session: AsyncSession, tracks: list, release_id: int):
  for track in tracks:
    track = Track(
      name=track["title"],
      side=track["position"],
      length=track["duration"],
      release_id=release_id,
    )
    session.add(track)
