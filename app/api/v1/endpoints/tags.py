from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.tag import TagCreate, TagUpdate, TagOut
from app.services.tag_service import get_tags, get_tag, create_tag, update_tag, delete_tag
from app.api.deps import get_current_user
from app.models.user import User
from typing import List
import uuid

router = APIRouter()


@router.get("", response_model=List[TagOut])
def list_tags(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_tags(db, current_user.id)


@router.post("", response_model=TagOut)
def create(data: TagCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return create_tag(db, data, current_user.id)


@router.put("/{tag_id}", response_model=TagOut)
def update(
    tag_id: uuid.UUID,
    data: TagUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = get_tag(db, tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return update_tag(db, tag, data)


@router.delete("/{tag_id}")
def delete(
    tag_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tag = get_tag(db, tag_id, current_user.id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    delete_tag(db, tag)
    return {"message": "Deleted"}
