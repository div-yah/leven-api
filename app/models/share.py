from sqlalchemy import Column, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from app.db.session import Base


class SharePermission(str, enum.Enum):
    view = "view"
    edit = "edit"


class Share(Base):
    __tablename__ = "shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    permission = Column(Enum(SharePermission), default=SharePermission.view, nullable=False)

    idea_id = Column(UUID(as_uuid=True), ForeignKey("ideas.id", ondelete="CASCADE"), nullable=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=True)
    shared_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    shared_with_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    idea = relationship("Idea", back_populates="shares", foreign_keys=[idea_id])
    category = relationship("Category", back_populates="shares", foreign_keys=[category_id])
    shared_by = relationship("User", back_populates="shares_given", foreign_keys=[shared_by_id])
    shared_with = relationship("User", back_populates="shares_received", foreign_keys=[shared_with_id])
