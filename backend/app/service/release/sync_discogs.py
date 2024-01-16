from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio.session import AsyncSession

from app.service.discogs import discogs_get_user_collection
from app.models import (
    Artist,
    Label,
    Release,
    Track,
    ArtistReleaseAssociation,
    LabelReleaseAssociation,
)
from app.core.logger import logger


async def sync_discogs(session: AsyncSession, username: str):
	collection = discogs_get_user_collection(username)

	for item in collection:
		if all(key in item for key in ["artists", "title", "labels"]):
				release_title = item["title"]
				release_stmt = await session.execute(
						select(Release).where(Release.name == release_title)
				)
				release = release_stmt.scalars().first()
				if not release:
						result = await session.execute(
								insert(Release).values(
										name=release_title,
										short=str(item["id"]),
										thumb=item["thumb"],
										year=item["year"],
										genre=item["genres"],
										styles=item["styles"],
										format=item["format"],
										purchased_at="discogs",
								)
						)
						release_id = result.inserted_primary_key[0]
						release = await session.get(Release, release_id)
						logger.info(f"Created release {release_title} with ID {release_id}")
				else:
						logger.info(f"Found release {release_title} with ID {release.id}")

				for artist_name in item["artists"]:
						artist_stmt = await session.execute(
								select(Artist).where(Artist.name == artist_name)
						)
						artist = artist_stmt.scalars().first()
						if not artist:
								result = await session.execute(
										insert(Artist).values(name=artist_name)
								)
								artist_id = result.inserted_primary_key[0]
								artist = await session.get(Artist, artist_id)
								logger.info(f"Created artist {artist_name} with ID {artist_id}")
						else:
								logger.info(f"Found artist {artist_name} with ID {artist.id}")

						await session.execute(
								insert(ArtistReleaseAssociation).values(
										artist_id=artist.id, release_id=release.id
								)
						)

				for label_name in item["labels"]:
						label_stmt = await session.execute(
								select(Label).where(Label.name == label_name)
						)
						label = label_stmt.scalars().first()
						if not label:
								result = await session.execute(
										insert(Label).values(name=label_name)
								)
								label_id = result.inserted_primary_key[0]
								label = await session.get(Label, label_id)
								logger.info(f"Created label {label_name} with ID {label_id}")
						else:
								logger.info(f"Found label {label_name} with ID {label.id}")

						await session.execute(
								insert(LabelReleaseAssociation).values(
										label_id=label.id, release_id=release.id
								)
						)

				for track in item["tracklist"]:
						await session.execute(
								insert(Track).values(
										name=track["title"],
										side=track["position"],
										length=track["duration"],
										release_id=release.id,
								)
						)

				await session.commit()
