import uuid

from sqlalchemy import Column, UUID, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, relationship

from app.db import Base
from app.models.label import Label
from app.models.artist import Artist

class Release(Base):
    __tablename__ = 'release'

    id: Mapped[UUID] = Column(UUID, primary_key=True, index=True, default=uuid.uuid4())

    name: Mapped[str] = Column(String)
    short: Mapped[str] = Column(String)

    label: Mapped["Label"] = relationship()
    label_id: Mapped[UUID] = Column(UUID, ForeignKey("label.id"))
    artist: Mapped["Artist"] = relationship()
    artist_id: Mapped[UUID] = Column(UUID, ForeignKey("artist.id"))

    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), onupdate=func.now())