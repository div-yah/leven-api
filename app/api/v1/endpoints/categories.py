from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut
from app.services.category_service import (
    get_root_categories, get_category, create_category, update_category, delete_category
)
from app.api.deps import get_current_user
from app.models.user import User
from typing import List
import uuid

router = APIRouter()


def enrich(cat, db) -> dict:
    data = {
        "id": cat.id,
        "name": cat.name,
        "description": cat.description,
        "color": cat.color,
        "icon": cat.icon,
        "order": cat.order,
        "owner_id": cat.owner_id,
        "parent_id": cat.parent_id,
        "created_at": cat.created_at,
        "updated_at": cat.updated_at,
        "idea_count": len(cat.ideas),
        "children": [enrich(child, db) for child in sorted(cat.children, key=lambda c: c.order)],
    }
    return data


@router.get("", response_model=List[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    roots = get_root_categories(db, current_user.id)
    return [enrich(c, db) for c in roots]


@router.post("", response_model=CategoryOut)
def create(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = create_category(db, data, current_user.id)
    return enrich(cat, db)


@router.put("/{category_id}", response_model=CategoryOut)
def update(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = get_category(db, category_id, current_user.id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat = update_category(db, cat, data)
    return enrich(cat, db)


@router.delete("/{category_id}")
def delete(
    category_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cat = get_category(db, category_id, current_user.id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    delete_category(db, cat)
    return {"message": "Deleted"}
