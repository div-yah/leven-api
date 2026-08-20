from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[UUID] = None
    order: int = 0


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    parent_id: Optional[UUID] = None
    order: Optional[int] = None


class CategoryOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    order: int
    owner_id: UUID
    parent_id: Optional[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    children: List["CategoryOut"] = []
    idea_count: int = 0

    class Config:
        from_attributes = True


CategoryOut.model_rebuild()
