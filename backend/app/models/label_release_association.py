from sqlalchemy import UUID, Column, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class LabelReleaseAssociation(Base):
  __tablename__ = "label_release"
  label_id = Column(UUID, ForeignKey("label.id"), primary_key=True)
  release_id = Column(UUID, ForeignKey("release.id"), primary_key=True)

  # Relationships
  label = relationship("Label", back_populates="releases")
  release = relationship("Release", back_populates="release_labels")
