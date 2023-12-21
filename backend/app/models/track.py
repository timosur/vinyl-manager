import uuid

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, relationship

from app.db import Base

class Track(Base):
    __tablename__ = "track"

    id: Mapped[UUID] = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)

    name: Mapped[str] = Column(String)
    side: Mapped[str] = Column(String)
    length: Mapped[int] = Column(Integer)
    rating: Mapped[int] = Column(Integer)
    genre: Mapped[str] = Column(String)
    bpm: Mapped[int] = Column(Integer)    
    key: Mapped[str] = Column(String)

    release_id: Mapped[UUID] = Column(UUID, ForeignKey("release.id"))
    release: Mapped["Release"] = relationship("Release", back_populates="tracks")

    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), onupdate=func.now())