from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    categories = relationship("Category", back_populates="owner", foreign_keys="Category.owner_id")
    ideas = relationship("Idea", back_populates="owner", foreign_keys="Idea.owner_id")
    comments = relationship("Comment", back_populates="owner", foreign_keys="Comment.owner_id")
    shares_given = relationship("Share", back_populates="shared_by", foreign_keys="Share.shared_by_id")
    shares_received = relationship("Share", back_populates="shared_with", foreign_keys="Share.shared_with_id")
