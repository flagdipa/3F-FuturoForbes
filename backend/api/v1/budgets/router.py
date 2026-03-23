from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime
import logging

from ....dependencies import get_db
from ....models import Budget, BudgetLine, TransactionSplit, Transaction, Category, User
from ...auth.deps import get_current_user

logger = logging.getLogger("api_budgets")
router = APIRouter()

class BudgetLineCreate(BaseModel):
    category_id: int
    allocated_amount: Decimal

class BudgetCreate(BaseModel):
    name: str
    period_type: str = "MONTHLY"
    start_date: date
    end_date: date
    notes: Optional[str] = None
    lines: List[BudgetLineCreate]

class BudgetStatusResponse(BaseModel):
    id: int
    category_name: str
    category_id: int
    allocated: float
    spent: float
    percentage: float
    status: str

@router.get("/")
def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budgets = db.exec(
        select(Budget).where(
            Budget.deleted_at == None,
            Budget.user_id == current_user.id
        )
    ).all()
    res = []
    for b in budgets:
        lines = db.exec(select(BudgetLine).where(BudgetLine.budget_id == b.id)).all()
        total_alloc = sum([float(l.allocated_amount) for l in lines])
        
        total_spent = 0.0
        # Calculate per line to be accurate
        for l in lines:
            sum_query = (
                select(func.sum(TransactionSplit.amount))
                .join(Transaction)
                .where(TransactionSplit.category_id == l.category_id)
                .where(Transaction.date >= b.start_date)
                .where(Transaction.date <= b.end_date)
                .where(Transaction.deleted_at == None)
                .where(TransactionSplit.amount < 0)
            )
            spent_val = db.exec(sum_query).first() or Decimal(0)
            total_spent += abs(float(spent_val))
            
        res.append({
            "id": b.id,
            "name": b.name,
            "period_type": b.period_type,
            "start_date": b.start_date,
            "end_date": b.end_date,
            "total_allocated": total_alloc,
            "total_spent": total_spent
        })
    return res

@router.post("/", response_model=dict)
def create_budget(
    b_in: BudgetCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = Budget(
        user_id=current_user.id,
        name=b_in.name,
        period_type=b_in.period_type,
        start_date=b_in.start_date,
        end_date=b_in.end_date,
        notes=b_in.notes
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    
    for l in b_in.lines:
        line = BudgetLine(
            budget_id=budget.id,
            category_id=l.category_id,
            allocated_amount=l.allocated_amount
        )
        db.add(line)
        
    db.commit()
    return {"message": "Presupuesto creado con éxito", "id": budget.id}

@router.delete("/{id}", response_model=dict)
def delete_budget(id: int, db: Session = Depends(get_db)):
    budget = db.get(Budget, id)
    if not budget or budget.deleted_at:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    
    budget.deleted_at = datetime.utcnow()
    db.add(budget)
    db.commit()
    return {"message": "Presupuesto borrado"}

@router.get("/{id}/status")
def get_budget_status(
    id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = db.get(Budget, id)
    if not budget or budget.deleted_at or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")

    res = []
    lines = db.exec(select(BudgetLine).where(BudgetLine.budget_id == id)).all()
    
    for l in lines:
        sum_query = (
            select(func.sum(TransactionSplit.amount))
            .join(Transaction)
            .where(TransactionSplit.category_id == l.category_id)
            .where(Transaction.date >= budget.start_date)
            .where(Transaction.date <= budget.end_date)
            .where(Transaction.deleted_at == None)
            .where(TransactionSplit.amount < 0)
        )
        spent = db.exec(sum_query).first() or Decimal(0)
        spent = abs(float(spent))
        alloc = float(l.allocated_amount)
        pct = (spent / alloc * 100) if alloc > 0 else 0
        
        status = "normal"
        if pct >= 100: status = "danger"
        elif pct >= 80: status = "warning"
        
        cat = db.get(Category, l.category_id)
        cname = cat.name if cat else f"Categoría {l.category_id}"

        res.append({
            "id": l.id,
            "category_id": l.category_id,
            "category_name": cname,
            "allocated": alloc,
            "spent": spent,
            "percentage": round(pct, 1),
            "status": status
        })
        
    return res

@router.post("/{id}/lines", response_model=dict)
def add_budget_line(
    id: int, 
    line_in: BudgetLineCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = db.get(Budget, id)
    if not budget or budget.deleted_at or budget.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
        
    line = BudgetLine(
        budget_id=id,
        category_id=line_in.category_id,
        allocated_amount=line_in.allocated_amount
    )
    db.add(line)
    db.commit()
    return {"message": "Línea de presupuesto añadida con éxito"}
