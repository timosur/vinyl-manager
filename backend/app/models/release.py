from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, relationship

from app.db import Base
from app.models.label import Label
from app.models.artist import Artist

class Release(Base):
    __tablename__ = 'release'

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String)
    short: Mapped[str] = Column(String)
    label: Mapped["Label"] = relationship(back_populates="release")
    artist: Mapped["Artist"] = relationship(back_populates="release")
    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), onupdate=func.now())