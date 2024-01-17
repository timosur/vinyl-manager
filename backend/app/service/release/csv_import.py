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
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio.session import AsyncSession


async def import_deejay_de(session: AsyncSession, file: UploadFile):
  try:
    # Read CSV from request body
    contents = file.file.read()
    buffer = StringIO(contents.decode("utf-8"))
    csv_rows = csv.DictReader(buffer, delimiter=";")
    csv_data = [row for row in csv_rows]

    release_ids = []
    for item in csv_data:
      if all(key in item for key in ["Artist", "Title", "Label", "Label No"]):
        # Check if release already exists
        release_stmt = await session.execute(
          select(Release).where(Release.name == item["Title"])
        )
        release = release_stmt.scalars().first()

        if release:
          logger.info(f"Found release {item['Title']} with ID {release.id}")
          logger.info(f"Skipping release {item['Title']}")
          continue

        # Get discogs release
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
        if (
          original_release is not None and
          (
            original_release["catno"].lower().replace(" ", "") != item["Label No"].lower().replace(" ", "") 
            or
            item["Label"].lower().replace(" ", "") not in original_release["all_labels"].lower().replace(" ", "")
          )
        ):
          logger.warning(
            f"Discogs release {original_release['title']} does not match deejay.de release {item['Title']}"
          )

          original_release = None
        
        # If discogs release is still not found, get tracklist from deejay.de
        if original_release is None:
          logger.info(f"Getting tracklist from deejay.de for {item['Title']}")
          
          # Call https://www.deejay.de/ajaxHelper/fp.php?t=item["ID"]&DEEJAY_SHOP=&s=
          # Get tracklist from response
          request_url = f"https://www.deejay.de/ajaxHelper/fp.php?t={item['ID']}&DEEJAY_SHOP=&s="
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
              side_track_split = part.split("\\")[-1].split("|")  # Splitting to get side and track number
              side_and_track_number = side_track_split[0].strip()  # Extracting the side and track number (e.g., A1, B2)
              track_name = side_track_split[1].strip()  # Extracting the track name
              tracks.append({
                "title": track_name,
                "position": side_and_track_number,
                "duration": None,
              })

          original_release = {
            "catno": item["Label No"],
            "thumb": None,
            "year": None,
            "genres": "Electronic",
            "styles": None,
            "format": "Vinyl",
            "tracklist": tracks
          }
        
        result = await session.execute(
          insert(Release).values(
            name=item["Title"],
            short=item["Label No"],
            thumb=original_release["thumb"],
            year=original_release["year"],
            genre=original_release["genres"],
            styles=original_release["styles"],
            format=original_release["format"],
            purchased_at="deejay.de",
          )
        )
        release_id = (
          result.inserted_primary_key[0]
          if result.inserted_primary_key is not None
          else None
        )

        if release_id is None:
          logger.warning(f"Could not create release {item['Title']}")
          continue

        logger.info(f"Created release {item['Title']} with ID {release_id}")
        release = await session.get(Release, release_id)

        # Check if artist exists, if not create it
        artist_stmt = await session.execute(
          select(Artist).where(Artist.name == item["Artist"])
        )
        artist = artist_stmt.scalars().first()
        if not artist:
          result = await session.execute(insert(Artist).values(name=item["Artist"]))
          artist_id = result.inserted_primary_key[0]
          artist = await session.get(Artist, artist_id)
          logger.info(f"Created artist {item['Artist']} with ID {artist_id}")
        else:
          logger.info(f"Found artist {item['Artist']} with ID {artist.id}")

        # Check if the Artist-Release association already exists
        assoc_exists_stmt = select(ArtistReleaseAssociation).where(
          ArtistReleaseAssociation.artist_id == artist.id,
          ArtistReleaseAssociation.release_id == release.id,
        )
        assoc_exists_result = await session.execute(assoc_exists_stmt)
        assoc_exists = assoc_exists_result.scalars().first()

        if not assoc_exists:
          # If the association does not exist, create it
          await session.execute(
            insert(ArtistReleaseAssociation).values(
              artist_id=artist.id, release_id=release.id
            )
          )

        # Check if label exists, if not create it
        label_stmt = await session.execute(
          select(Label).where(Label.name == item["Label"])
        )
        label = label_stmt.scalars().first()
        if not label:
          result = await session.execute(insert(Label).values(name=item["Label"]))
          label_id = result.inserted_primary_key[0]
          label = await session.get(Label, label_id)
          logger.info(f"Created label {item['Label']} with ID {label_id}")
        else:
          logger.info(f"Found label {item['Label']} with ID {label.id}")

        # Check if the Label-Release association already exists
        assoc_exists_stmt = select(LabelReleaseAssociation).where(
          LabelReleaseAssociation.label_id == label.id,
          LabelReleaseAssociation.release_id == release.id,
        )
        assoc_exists_result = await session.execute(assoc_exists_stmt)
        assoc_exists = assoc_exists_result.scalars().first()

        if not assoc_exists:
          # If the association does not exist, create it
          await session.execute(
            insert(LabelReleaseAssociation).values(
              label_id=label.id, release_id=release.id
            )
          )

        # Process tracklist from discogs
        if original_release["tracklist"] is not None:
          for track in original_release["tracklist"]:
            logger.info(f"Adding track {track['title']} to release {release.name}")
            await session.execute(
              insert(Track).values(
                name=track["title"],
                side=track["position"],
                length=track["duration"],
                release_id=release.id,
              )
            )

        await session.commit()
        release_ids.append(release_id)

    return release_ids

  except Exception as e:
    raise e
