from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class TagCreate(BaseModel):
    name: str
    color: Optional[str] = None


class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None


class TagOut(BaseModel):
    id: UUID
    name: str
    color: Optional[str]
    owner_id: UUID
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
