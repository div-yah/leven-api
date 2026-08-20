from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.share import SharePermission
from app.schemas.user import UserOut


class ShareCreate(BaseModel):
    shared_with_id: UUID
    permission: SharePermission = SharePermission.view
    idea_id: Optional[UUID] = None
    category_id: Optional[UUID] = None


class ShareOut(BaseModel):
    id: UUID
    permission: SharePermission
    idea_id: Optional[UUID]
    category_id: Optional[UUID]
    shared_by_id: UUID
    shared_with_id: UUID
    shared_with: UserOut
    created_at: datetime

    class Config:
        from_attributes = True
