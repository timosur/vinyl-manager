import csv
from io import StringIO
from fastapi import UploadFile
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select, insert

from app.models import (
    Artist,
    Label,
    Release,
    Track,
    ArtistReleaseAssociation,
    LabelReleaseAssociation,
)
from app.service.discogs import discogs_search_tracklist
from app.core.logger import logger


async def import_deejay_de(session: AsyncSession, file: UploadFile):
    try:
        # Read CSV from request body
        contents = file.file.read()
        buffer = StringIO(contents.decode("utf-8"))
        csv_rows = csv.DictReader(buffer, delimiter=";")
        csv_data = [row for row in csv_rows]

        print(csv_data)

        release_ids = []
        for item in csv_data:
            if all(key in item for key in ["Artist", "Title", "Label", "Label No"]):
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
                        )
                    )
                    release_id = result.inserted_primary_key[0]
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
                    result = await session.execute(
                        insert(Artist).values(name=item["Artist"])
                    )
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
                    result = await session.execute(
                        insert(Label).values(name=item["Label"])
                    )
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
                tracklist = discogs_search_tracklist(
                    f"{item['Artist']} {item['Title']} {item['Label']}"
                )

                if tracklist is not None:
                    for track in tracklist:
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
