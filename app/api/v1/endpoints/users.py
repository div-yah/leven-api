from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.user import UserOut, UserUpdate
from app.services.user_service import search_users, update_user
from app.api.deps import get_current_user
from app.models.user import User
from typing import List

router = APIRouter()


@router.get("/search", response_model=List[UserOut])
def search(
    q: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return search_users(db, q, current_user.id)


@router.put("/me", response_model=UserOut)
def update_me(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return update_user(db, current_user, data)
