from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped
from app.db import Base

class Artist(Base):
    __tablename__ = 'artist'

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    name: Mapped[str] = Column(String)
    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), onupdate=func.now())