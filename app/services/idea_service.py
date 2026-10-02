from sqlalchemy.orm import Session
from app.models.idea import Idea, IdeaStatus, IdeaContentType
from app.models.tag import Tag
from app.schemas.idea import IdeaCreate, IdeaUpdate
from app.services.link_metadata import fetch_link_preview_image
from typing import Optional, List
import uuid


def get_ideas(
    db: Session,
    owner_id: uuid.UUID,
    category_id: Optional[uuid.UUID] = None,
    status: Optional[IdeaStatus] = None,
    tag_id: Optional[uuid.UUID] = None,
    search: Optional[str] = None,
) -> List[Idea]:
    q = db.query(Idea).filter(Idea.owner_id == owner_id)
    if category_id is not None:
        q = q.filter(Idea.category_id == category_id)
    else:
        # root level: no category
        pass
    if status:
        q = q.filter(Idea.status == status)
    if tag_id:
        q = q.filter(Idea.tags.any(Tag.id == tag_id))
    if search:
        q = q.filter(Idea.title.ilike(f"%{search}%") | Idea.content.ilike(f"%{search}%"))
    return q.order_by(Idea.created_at.desc()).all()


def get_root_ideas(db: Session, owner_id: uuid.UUID) -> List[Idea]:
    return (
        db.query(Idea)
        .filter(Idea.owner_id == owner_id, Idea.category_id == None)
        .order_by(Idea.created_at.desc())
        .all()
    )


def get_ideas_in_category(db: Session, category_id: uuid.UUID, owner_id: uuid.UUID) -> List[Idea]:
    return (
        db.query(Idea)
        .filter(Idea.category_id == category_id, Idea.owner_id == owner_id)
        .order_by(Idea.created_at.desc())
        .all()
    )


def get_idea(db: Session, idea_id: uuid.UUID) -> Optional[Idea]:
    return db.query(Idea).filter(Idea.id == idea_id).first()


def create_idea(db: Session, data: IdeaCreate, owner_id: uuid.UUID) -> Idea:
    tag_ids = data.tag_ids
    idea_data = data.model_dump(exclude={"tag_ids"})
    idea = Idea(**idea_data, owner_id=owner_id)

    if (
        idea.content_type == IdeaContentType.link
        and idea.link
        and not idea.image_url
    ):
        idea.image_url = fetch_link_preview_image(idea.link)

    if tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids), Tag.owner_id == owner_id).all()
        idea.tags = tags
    db.add(idea)
    db.commit()
    db.refresh(idea)
    return idea


def update_idea(db: Session, idea: Idea, data: IdeaUpdate, owner_id: uuid.UUID) -> Idea:
    update_data = data.model_dump(exclude_unset=True)
    tag_ids = update_data.pop("tag_ids", None)

    link_changed = "link" in update_data and update_data["link"] != idea.link
    image_url_explicitly_set = "image_url" in update_data

    for field, value in update_data.items():
        setattr(idea, field, value)

    if (
        idea.content_type == IdeaContentType.link
        and idea.link
        and not image_url_explicitly_set
        and (link_changed or not idea.image_url)
    ):
        idea.image_url = fetch_link_preview_image(idea.link)

    if tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(tag_ids), Tag.owner_id == owner_id).all()
        idea.tags = tags
    db.commit()
    db.refresh(idea)
    return idea


def delete_idea(db: Session, idea: Idea):
    db.delete(idea)
    db.commit()
