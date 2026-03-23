from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...dependencies import get_db
from ...models import Institution, User
from ..auth.deps import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class InstitutionCreate(BaseModel):
    name: str
    type: Optional[str] = None
    icon: Optional[str] = None

class InstitutionResponse(InstitutionCreate):
    id: int

@router.get("/", response_model=List[InstitutionResponse])
def list_institutions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    institutions = db.exec(select(Institution).where(Institution.deleted_at == None, Institution.user_id == current_user.id)).all()
    return institutions

@router.post("/", response_model=InstitutionResponse)
def create_institution(institution_in: InstitutionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    institution = Institution(
        **institution_in.model_dump(),
        user_id=current_user.id
    )
    db.add(institution)
    db.commit()
    db.refresh(institution)
    return institution

@router.put("/{id}", response_model=InstitutionResponse)
def update_institution(id: int, institution_in: InstitutionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    institution = db.get(Institution, id)
    if not institution or institution.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Institution not found")
        
    for key, value in institution_in.model_dump(exclude_unset=True).items():
        setattr(institution, key, value)
        
    db.add(institution)
    db.commit()
    db.refresh(institution)
    return institution

@router.delete("/{id}")
def delete_institution(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    institution = db.get(Institution, id)
    if not institution or institution.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Institution not found")
        
    institution.deleted_at = datetime.utcnow()
    db.add(institution)
    db.commit()
    return {"status": "success"}
