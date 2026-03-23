from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...dependencies import get_db
from ...models import Payee, User
from ..auth.deps import get_current_user
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class PayeeCreate(BaseModel):
    name: str
    code: str
    default_category_id: Optional[int] = None
    bank_name: Optional[str] = None
    cbu: Optional[str] = None
    cuit: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True

class PayeeResponse(PayeeCreate):
    id: int
    has_transactions: bool = False

@router.get("/", response_model=List[PayeeResponse])
def list_payees(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payees = db.exec(select(Payee).where(Payee.deleted_at == None, Payee.user_id == current_user.id)).all()
    results = []
    for p in payees:
        p_dict = p.model_dump()
        p_dict["id"] = p.id
        p_dict["is_active"] = p.is_active
        # Evaluates boolean based on relationship
        p_dict["has_transactions"] = len(p.transactions) > 0
        results.append(PayeeResponse(**p_dict))
    return results

@router.post("/", response_model=PayeeResponse)
def create_payee(payee_in: PayeeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payee = Payee(
        **payee_in.model_dump(),
        user_id=current_user.id
    )
    db.add(payee)
    db.commit()
    db.refresh(payee)
    return payee

@router.put("/{id}", response_model=PayeeResponse)
def update_payee(id: int, payee_in: PayeeCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payee = db.get(Payee, id)
    if not payee or payee.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payee not found")
        
    for key, value in payee_in.model_dump(exclude_unset=True).items():
        setattr(payee, key, value)
        
    db.add(payee)
    db.commit()
    db.refresh(payee)
    return payee

@router.delete("/{id}")
def delete_payee(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    payee = db.get(Payee, id)
    if not payee or payee.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Payee not found")
        
    if len(payee.transactions) > 0:
        raise HTTPException(status_code=400, detail="No se puede eliminar un beneficiario con transacciones asociadas")
        
    payee.deleted_at = datetime.utcnow()
    db.add(payee)
    db.commit()
    return {"status": "success"}
