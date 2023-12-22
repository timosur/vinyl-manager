from typing import List
import uuid

from sqlalchemy import Column, UUID, String, DateTime, LargeBinary
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, relationship

from app.db import Base
from app.models.label import Label
from app.models.artist import Artist
from app.models.track import Track

class Release(Base):
    __tablename__ = 'release'

    id: Mapped[UUID] = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)

    name: Mapped[str] = Column(String)
    short: Mapped[str] = Column(String)
    notes: Mapped[str] = Column(String)
    audio: Mapped[bytes] = Column(LargeBinary)  # Define the Blob Audio column
    
    labels: Mapped[List[Label]] = relationship("Label", back_populates="release")
    artists: Mapped[List[Artist]] = relationship("Artist", back_populates="release")
    tracks: Mapped[List[Track]] = relationship("Track", back_populates="release")

    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), onupdate=func.now())