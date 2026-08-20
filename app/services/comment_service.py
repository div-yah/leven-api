from sqlalchemy.orm import Session
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate
from typing import List, Optional
import uuid


def get_comments_for_idea(db: Session, idea_id: uuid.UUID) -> List[Comment]:
    # Return only top-level comments; replies come via relationship
    return (
        db.query(Comment)
        .filter(Comment.idea_id == idea_id, Comment.parent_id == None)
        .order_by(Comment.created_at.asc())
        .all()
    )


def get_comment(db: Session, comment_id: uuid.UUID) -> Optional[Comment]:
    return db.query(Comment).filter(Comment.id == comment_id).first()


def create_comment(db: Session, data: CommentCreate, idea_id: uuid.UUID, owner_id: uuid.UUID) -> Comment:
    comment = Comment(**data.model_dump(), idea_id=idea_id, owner_id=owner_id)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def update_comment(db: Session, comment: Comment, data: CommentUpdate) -> Comment:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return comment


def delete_comment(db: Session, comment: Comment):
    db.delete(comment)
    db.commit()
