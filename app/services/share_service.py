from sqlalchemy.orm import Session
from app.models.share import Share
from app.schemas.share import ShareCreate
from typing import List
import uuid


def create_share(db: Session, data: ShareCreate, shared_by_id: uuid.UUID) -> Share:
    share = Share(**data.model_dump(), shared_by_id=shared_by_id)
    db.add(share)
    db.commit()
    db.refresh(share)
    return share


def get_shares_for_idea(db: Session, idea_id: uuid.UUID) -> List[Share]:
    return db.query(Share).filter(Share.idea_id == idea_id).all()


def get_shares_received(db: Session, user_id: uuid.UUID) -> List[Share]:
    return db.query(Share).filter(Share.shared_with_id == user_id).all()


def get_share(db: Session, share_id: uuid.UUID) -> Share:
    return db.query(Share).filter(Share.id == share_id).first()


def delete_share(db: Session, share: Share):
    db.delete(share)
    db.commit()
