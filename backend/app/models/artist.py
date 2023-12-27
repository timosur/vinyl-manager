import uuid

from sqlalchemy import Column, UUID, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, relationship
from app.db import Base  

class Artist(Base):
    __tablename__ = 'artist'

    id: Mapped[UUID] = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)

    name: Mapped[str] = Column(String)

    artist_releases = relationship('ArtistReleaseAssociation', back_populates='artist')

    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), onupdate=func.now())