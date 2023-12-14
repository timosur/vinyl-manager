import uuid

from sqlalchemy import Column, UUID, ForeignKey, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, relationship
from app.db import Base

class Label(Base):
    __tablename__ = 'label'

    id: Mapped[UUID] = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)

    name: Mapped[str] = Column(String)

    release_id: Mapped[UUID] = Column(UUID, ForeignKey("release.id"))
    release: Mapped["Release"] = relationship("Release", back_populates="labels")

    created_at: Mapped[DateTime] = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), onupdate=func.now())