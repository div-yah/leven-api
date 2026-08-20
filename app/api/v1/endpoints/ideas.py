from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.idea import IdeaCreate, IdeaUpdate, IdeaOut
from app.services.idea_service import (
    get_ideas, get_root_ideas, get_ideas_in_category, get_idea, create_idea, update_idea, delete_idea
)
from app.models.idea import IdeaStatus
from app.api.deps import get_current_user
from app.models.user import User
from typing import List, Optional
import uuid

router = APIRouter()


def enrich(idea) -> dict:
    return {
        "id": idea.id,
        "title": idea.title,
        "content": idea.content,
        "link": idea.link,
        "image_url": idea.image_url,
        "content_type": idea.content_type,
        "status": idea.status,
        "owner_id": idea.owner_id,
        "category_id": idea.category_id,
        "tags": idea.tags,
        "created_at": idea.created_at,
        "updated_at": idea.updated_at,
        "comment_count": len(idea.comments),
    }


@router.get("", response_model=List[IdeaOut])
def list_ideas(
    category_id: Optional[uuid.UUID] = Query(None),
    root_only: bool = Query(False),
    status: Optional[IdeaStatus] = Query(None),
    tag_id: Optional[uuid.UUID] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if root_only:
        ideas = get_root_ideas(db, current_user.id)
    elif category_id:
        ideas = get_ideas_in_category(db, category_id, current_user.id)
    else:
        ideas = get_ideas(db, current_user.id, status=status, tag_id=tag_id, search=search)
    return [enrich(i) for i in ideas]


@router.post("", response_model=IdeaOut)
def create(
    data: IdeaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    idea = create_idea(db, data, current_user.id)
    return enrich(idea)


@router.get("/{idea_id}", response_model=IdeaOut)
def get_one(
    idea_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    idea = get_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return enrich(idea)


@router.put("/{idea_id}", response_model=IdeaOut)
def update(
    idea_id: uuid.UUID,
    data: IdeaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    idea = get_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    idea = update_idea(db, idea, data, current_user.id)
    return enrich(idea)


@router.delete("/{idea_id}")
def delete(
    idea_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    idea = get_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    if idea.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    delete_idea(db, idea)
    return {"message": "Deleted"}
