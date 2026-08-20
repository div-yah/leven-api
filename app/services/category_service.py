from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from typing import Optional, List
import uuid


def get_categories_for_user(db: Session, owner_id: uuid.UUID) -> List[Category]:
    return db.query(Category).filter(Category.owner_id == owner_id).all()


def get_root_categories(db: Session, owner_id: uuid.UUID) -> List[Category]:
    return (
        db.query(Category)
        .filter(Category.owner_id == owner_id, Category.parent_id == None)
        .order_by(Category.order)
        .all()
    )


def get_category(db: Session, category_id: uuid.UUID, owner_id: uuid.UUID) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id, Category.owner_id == owner_id).first()


def get_category_by_id(db: Session, category_id: uuid.UUID) -> Optional[Category]:
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, data: CategoryCreate, owner_id: uuid.UUID) -> Category:
    category = Category(**data.model_dump(), owner_id=owner_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update_category(db: Session, category: Category, data: CategoryUpdate) -> Category:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category):
    db.delete(category)
    db.commit()


def build_tree(categories: List[Category]) -> List[Category]:
    """Return only root categories — children are already lazy-loaded via relationship."""
    return [c for c in categories if c.parent_id is None]
