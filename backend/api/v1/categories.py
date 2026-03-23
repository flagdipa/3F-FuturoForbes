from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...dependencies import get_db
from ...models import Category, User
from ..auth.deps import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class CategoryCreate(BaseModel):
    name: str
    type: str # INCOME, EXPENSE
    parent_id: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    notes: Optional[str] = None

class CategoryResponse(CategoryCreate):
    id: int

@router.get("/", response_model=List[CategoryResponse])
def list_categories(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    categories = db.exec(select(Category).where(Category.deleted_at == None, Category.user_id == current_user.id)).all()
    return categories

@router.post("/", response_model=CategoryResponse)
def create_category(category_in: CategoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    category = Category(
        **category_in.model_dump(),
        user_id=current_user.id
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@router.delete("/{id}")
def delete_category(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    category = db.get(Category, id)
    if not category or category.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Category not found")
    category.deleted_at = datetime.utcnow()
    db.add(category)
    db.commit()
    return {"status": "success"}
