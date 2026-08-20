from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.share import ShareCreate, ShareOut
from app.services.share_service import create_share, get_shares_for_idea, get_shares_received, get_share, delete_share
from app.api.deps import get_current_user
from app.models.user import User
from typing import List
import uuid

router = APIRouter()


@router.post("", response_model=ShareOut)
def create(
    data: ShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not data.idea_id and not data.category_id:
        raise HTTPException(status_code=400, detail="Must specify idea_id or category_id")
    return create_share(db, data, current_user.id)


@router.get("/received", response_model=List[ShareOut])
def received(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_shares_received(db, current_user.id)


@router.get("/idea/{idea_id}", response_model=List[ShareOut])
def idea_shares(
    idea_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_shares_for_idea(db, idea_id)


@router.delete("/{share_id}")
def revoke(
    share_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    share = get_share(db, share_id)
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    if share.shared_by_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    delete_share(db, share)
    return {"message": "Share revoked"}
