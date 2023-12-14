import csv
from io import StringIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select, insert

from app.models import Artist, Label, Release, Track
from app.service.discogs import discogs_search_tracklist
from app.core.logger import logger

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
            # check if artist exists, if not create it
            artist_stmt = await session.execute(
                select(Artist).where(Artist.name == item["Artist"])
            )
            artist = artist_stmt.scalars().first()
            if not artist:
                result = await session.execute(
                    insert(Artist).values(name=item["Artist"])
                )

                # Retrieve the primary key (ID) of the newly inserted artist
                artist_id = result.inserted_primary_key[0]

                logger.info(f"Created artist {item['Artist']} with ID {artist_id}")
            else:
                artist_id = artist.id

                logger.info(f"Found artist {item['Artist']} with ID {artist_id}")

            # check if label exists, if not create it
            label_stmt = await session.execute(
                select(Label).where(Label.name == item["Label"])
            )
            label = label_stmt.scalars().first()
            if not label:
                result = await session.execute(
                    insert(Label).values(name=item["Label"])
                )

                # Retrieve the primary key (ID) of the newly inserted label
                label_id = result.inserted_primary_key[0]

                logger.info(f"Created label {item['Label']} with ID {label_id}")
            else:
                label_id = label.id

                logger.info(f"Found label {item['Label']} with ID {label_id}")

            # check if release exists, if not create it
            release_stmt = await session.execute(
                select(Release).where(Release.name == item["Title"])
            )
            release = release_stmt.scalars().first()
            if not release:
                result = await session.execute(
                    insert(Release).values(
                        name=item["Title"],
                        short=item["Label No"],
                        artist_id=artist_id,
                        label_id=label_id,
                    )
                )

                # Retrieve the primary key (ID) of the newly inserted record
                release_id = result.inserted_primary_key[0]

                logger.info(f"Created release {item['Title']} with ID {release_id}")

                release_ids.append(release_id)
            else:
                release_id = release.id

                logger.info(f"Found release {item['Title']} with ID {release_id}")

            # grab track for the release via discogs
            tracklist = discogs_search_tracklist(f"{item['Label No']} {item['Title']}")

            if tracklist is not None:
                for track in tracklist:
                    # check if track exists, if not create it
                    found_track_stmt = await session.execute(
                        select(Track).where(Track.name == track["title"])
                    )
                    found_track = found_track_stmt.scalars().first()

                    if not found_track:
                        result = await session.execute(
                            insert(Track).values(
                                name=track["title"],
                                side=track["position"],
                                length=track["duration"],
                                release_id=release_id,
                            )
                        )

                        # Retrieve the primary key (ID) of the newly inserted track
                        track_id = result.inserted_primary_key[0]

                        logger.info(
                            f"Created track {track['title']} with ID {track_id}"
                        )
                    else:
                        logger.info(
                            f"Found track {track['title']} with ID {found_track.id}"
                        )

            await session.commit()

    return release_ids

  except Exception as e:
      logger.exception(e)
      
      raise e