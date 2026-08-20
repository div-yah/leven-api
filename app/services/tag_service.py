from sqlalchemy.orm import Session
from app.models.tag import Tag
from app.schemas.tag import TagCreate, TagUpdate
from typing import List, Optional
import uuid


def get_tags(db: Session, owner_id: uuid.UUID) -> List[Tag]:
    return db.query(Tag).filter(Tag.owner_id == owner_id).order_by(Tag.name).all()


def get_tag(db: Session, tag_id: uuid.UUID, owner_id: uuid.UUID) -> Optional[Tag]:
    return db.query(Tag).filter(Tag.id == tag_id, Tag.owner_id == owner_id).first()


def create_tag(db: Session, data: TagCreate, owner_id: uuid.UUID) -> Tag:
    tag = Tag(**data.model_dump(), owner_id=owner_id)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


def update_tag(db: Session, tag: Tag, data: TagUpdate) -> Tag:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tag, field, value)
    db.commit()
    db.refresh(tag)
    return tag


def delete_tag(db: Session, tag: Tag):
    db.delete(tag)
    db.commit()
