from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.session import Base
from app.models.tag import idea_tags


class IdeaStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    archived = "archived"


class IdeaContentType(str, enum.Enum):
    text = "text"
    link = "link"
    image = "image"


class Idea(Base):
    __tablename__ = "ideas"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    link = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    content_type = Column(Enum(IdeaContentType), default=IdeaContentType.text, nullable=False)
    status = Column(Enum(IdeaStatus), default=IdeaStatus.draft, nullable=False)

    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="ideas", foreign_keys=[owner_id])
    category = relationship("Category", back_populates="ideas")
    tags = relationship("Tag", secondary=idea_tags, back_populates="ideas")
    comments = relationship("Comment", back_populates="idea", cascade="all, delete-orphan")
    shares = relationship("Share", back_populates="idea", foreign_keys="Share.idea_id")
