from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.service.discogs import discogs_get_user_collection
from app.models import Artist, Label, Release, Track
from app.core.logger import logger

async def sync_discogs(session: AsyncSession, username: str):
  collection = discogs_get_user_collection(username)

  for item in collection:
    # Check if the required keys are present in the item
    if all(key in item for key in ["artists", "title", "labels"]):
        # Process the artist
        artist_name = item["artists"]
        artist_stmt = await session.execute(
            select(Artist).where(Artist.name == artist_name)
        )
        artist = artist_stmt.scalars().first()
        if not artist:
            result = await session.execute(
                insert(Artist).values(name=artist_name)
            )
            artist_id = result.inserted_primary_key[0]
            logger.info(f"Created artist {artist_name} with ID {artist_id}")
        else:
            artist_id = artist.id
            logger.info(f"Found artist {artist_name} with ID {artist_id}")

        # Process the label
        label_name = item["labels"]
        label_stmt = await session.execute(
            select(Label).where(Label.name == label_name)
        )
        label = label_stmt.scalars().first()
        if not label:
            result = await session.execute(
                insert(Label).values(name=label_name)
            )
            label_id = result.inserted_primary_key[0]
            logger.info(f"Created label {label_name} with ID {label_id}")
        else:
            label_id = label.id
            logger.info(f"Found label {label_name} with ID {label_id}")

        # Process the release
        release_title = item["title"]
        release_stmt = await session.execute(
            select(Release).where(Release.name == release_title)
        )
        release = release_stmt.scalars().first()
        if not release:
            result = await session.execute(
                insert(Release).values(
                    name=release_title,
                    short=item["year"],  # Assuming 'year' is equivalent to 'Label No'
                    artist_id=artist_id,
                    label_id=label_id,
                )
            )
            release_id = result.inserted_primary_key[0]
            logger.info(f"Created release {release_title} with ID {release_id}")
        else:
            release_id = release.id
            logger.info(f"Found release {release_title} with ID {release_id}")

        # Process tracklist
        tracklist = item["tracklist"]
        for track in tracklist:
            track_title = track["title"]
            found_track_stmt = await session.execute(
                select(Track).where(Track.name == track_title)
            )
            found_track = found_track_stmt.scalars().first()
            if not found_track:
                result = await session.execute(
                    insert(Track).values(
                        name=track_title,
                        side=track["position"],
                        length=track["duration"],
                        release_id=release_id,
                    )
                )
                track_id = result.inserted_primary_key[0]
                logger.info(f"Created track {track_title} with ID {track_id}")
            else:
                logger.info(f"Found track {track_title} with ID {found_track.id}")

        await session.commit()
