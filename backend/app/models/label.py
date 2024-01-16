import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from app.db import Base
from app.models.label_release_association import LabelReleaseAssociation


class Label(Base):
  __tablename__ = "label"

  id: Mapped[UUID] = Column(UUID, primary_key=True, index=True, default=uuid.uuid4)

  name: Mapped[str] = Column(String)

  releases = relationship("LabelReleaseAssociation", back_populates="label")

  created_at: Mapped[DateTime] = Column(
    DateTime(timezone=True), server_default=func.now()
  )
  updated_at: Mapped[DateTime] = Column(DateTime(timezone=True), onupdate=func.now())
