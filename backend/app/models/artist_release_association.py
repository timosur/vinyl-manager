from sqlalchemy import UUID, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class ArtistReleaseAssociation(Base):
  __tablename__ = "artist_release"
  artist_id = Column(UUID, ForeignKey("artist.id"), primary_key=True)
  release_id = Column(UUID, ForeignKey("release.id"), primary_key=True)

  # Relationships
  artist = relationship("Artist", back_populates="artist_releases")
  release = relationship("Release", back_populates="release_artists")
