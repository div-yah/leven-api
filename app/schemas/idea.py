from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.models.idea import IdeaStatus, IdeaContentType
from app.schemas.tag import TagOut


class IdeaCreate(BaseModel):
    title: str
    content: Optional[str] = None
    link: Optional[str] = None
    image_url: Optional[str] = None
    content_type: IdeaContentType = IdeaContentType.text
    status: IdeaStatus = IdeaStatus.draft
    category_id: Optional[UUID] = None
    tag_ids: List[UUID] = []


class IdeaUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    link: Optional[str] = None
    image_url: Optional[str] = None
    content_type: Optional[IdeaContentType] = None
    status: Optional[IdeaStatus] = None
    category_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None


class IdeaOut(BaseModel):
    id: UUID
    title: str
    content: Optional[str]
    link: Optional[str]
    image_url: Optional[str]
    content_type: IdeaContentType
    status: IdeaStatus
    owner_id: UUID
    category_id: Optional[UUID]
    tags: List[TagOut] = []
    created_at: datetime
    updated_at: Optional[datetime]
    comment_count: int = 0

    class Config:
        from_attributes = True
