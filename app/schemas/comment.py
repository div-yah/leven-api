from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.user import UserOut


class CommentCreate(BaseModel):
    content: str
    image_url: Optional[str] = None
    parent_id: Optional[UUID] = None


class CommentUpdate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None


class CommentOut(BaseModel):
    id: UUID
    content: str
    image_url: Optional[str]
    idea_id: UUID
    owner_id: UUID
    parent_id: Optional[UUID]
    owner: UserOut
    replies: List["CommentOut"] = []
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


CommentOut.model_rebuild()
