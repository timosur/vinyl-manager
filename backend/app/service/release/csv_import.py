import csv
from io import StringIO

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
        # Get discogs release
        discogs_release = discogs_search_release(f"{item['Title']} {item['Label No']}")

        if discogs_release is None:
          logger.warning(
            f"Could not find discogs release for {item['Title']} {item['Label No']}"
          )

          # Try again without the label number
          discogs_release = discogs_search_release(item["Title"])

          if discogs_release is None:
            logger.warning(f"Could not find discogs release for {item['Title']}")
            logger.warning(f"Skipping {item['Title']}...")

            continue

        # Check if release catno matches Label No, remove all whitespace, lowercase
        if (
          discogs_release["catno"].replace(" ", "").lower()
          != item["Label No"].replace(" ", "").lower()
        ):
          logger.warning(
            f"Discogs release catno {discogs_release['catno']} does not match Label No {item['Label No']}"
          )
          logger.warning(f"Skipping {item['Title']}...")

          continue

        # Check if release exists, if not create it
        release_stmt = await session.execute(
          select(Release).where(Release.name == item["Title"])
        )
        release = release_stmt.scalars().first()
        if not release:
          result = await session.execute(
            insert(Release).values(
              name=item["Title"],
              short=item["Label No"],
              thumb=discogs_release["thumb"],
              year=discogs_release["year"],
              genre=discogs_release["genres"],
              styles=discogs_release["styles"],
              format=discogs_release["format"],
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
        else:
          release_id = release.id
          logger.info(f"Found release {item['Title']} with ID {release_id}")

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
        if discogs_release["tracklist"] is not None:
          for track in discogs_release["tracklist"]:
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
