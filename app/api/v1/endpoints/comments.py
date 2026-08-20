from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.comment import CommentCreate, CommentUpdate, CommentOut
from app.services.comment_service import (
    get_comments_for_idea, get_comment, create_comment, update_comment, delete_comment
)
from app.services.idea_service import get_idea
from app.api.deps import get_current_user
from app.models.user import User
from typing import List
import uuid

router = APIRouter()


@router.get("/ideas/{idea_id}/comments", response_model=List[CommentOut])
def list_comments(
    idea_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    idea = get_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return get_comments_for_idea(db, idea_id)


@router.post("/ideas/{idea_id}/comments", response_model=CommentOut)
def create(
    idea_id: uuid.UUID,
    data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    idea = get_idea(db, idea_id)
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return create_comment(db, data, idea_id, current_user.id)


@router.put("/comments/{comment_id}", response_model=CommentOut)
def update(
    comment_id: uuid.UUID,
    data: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return update_comment(db, comment, data)


@router.delete("/comments/{comment_id}")
def delete(
    comment_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    comment = get_comment(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    delete_comment(db, comment)
    return {"message": "Deleted"}
