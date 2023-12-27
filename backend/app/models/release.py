import uuid

from sqlalchemy import Column, UUID, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, relationship

from app.db import Base

class Release(Base):
    __tablename__ = 'release'

    id: Mapped[UUID] = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)

    name: Mapped[str] = Column(String)
    short: Mapped[str] = Column(String)
    notes: Mapped[str] = Column(String)
    
    release_artists = relationship('ArtistReleaseAssociation', back_populates='release')
    release_labels = relationship('LabelReleaseAssociation', back_populates='release')

    tracks = relationship("Track", back_populates="release")

    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), onupdate=func.now())