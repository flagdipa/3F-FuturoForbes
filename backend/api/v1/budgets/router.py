from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from sqlmodel import select, func
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime
import logging

from ....dependencies import get_db
from ....models import Budget, BudgetLine, TransactionSplit, Transaction

logger = logging.getLogger("api_budgets")
router = APIRouter()

# SCEMAS REQUERIDOS
class BudgetLineCreate(BaseModel):
    category_id: int

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
    status: str # ontrack, warning, overbudget

@router.get("/")
def get_budgets(db: Session = Depends(get_db)):
    budgets = db.exec(select(Budget).where(Budget.deleted_at == None)).all()
    # Mock some data for frontend display until fully populated
    if not budgets:
        return [
            {
                "id": 1,
                "name": f"Presupuesto de {datetime.now().strftime('%B %Y')}",
                "period_type": "MONTHLY",
                "start_date": datetime.now().replace(day=1).date(),
                "end_date": datetime.now().date(),
                "total_allocated": 1500000.00,
                "total_spent": 1200000.00
            }
        ]
    return budgets

@router.post("/", response_model=dict)
def create_budget(b_in: BudgetCreate, db: Session = Depends(get_db)):
    budget = Budget(
        user_id=1,
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

@router.get("/{id}/status")
def get_budget_status(id: int, db: Session = Depends(get_db)):
    """
    Calcula en tiempo real cuánto del presupuesto asignado se ha gastado.
    Busca transacciones que caen dentro de las fechas de `start_date` y `end_date` del Budget.
    """
    budget = db.get(Budget, id)
    if not budget or budget.deleted_at:
        # Mock logic to avoid frontend crash if DB is empty
        return _mock_budget_status()

    # Logica cruda teorica:
    # 1. Obtener lineas
    # 2. Sumar transacciones de esa categoria en ese daterange
    res = []
    lines = db.exec(select(BudgetLine).where(BudgetLine.budget_id == id)).all()
    
    for l in lines:
        # Sum transactions for this category in date range
        sum_query = (
            select(func.sum(TransactionSplit.amount))
            .join(Transaction)
            .where(TransactionSplit.category_id == l.category_id)
            .where(Transaction.date >= budget.start_date)
            .where(Transaction.date <= budget.end_date)
        )
        spent = db.exec(sum_query).first() or Decimal(0)
        # Spent usually is negative, so abs it
        spent = abs(float(spent))
        alloc = float(l.allocated_amount)
        pct = (spent / alloc * 100) if alloc > 0 else 0
        
        status = "ontrack"
        if pct > 100: status = "overbudget"
        elif pct > 80: status = "warning"
        
        res.append({
            "id": l.id,
            "category_id": l.category_id,
            "category_name": f"Categoría {l.category_id}", # Idealmente hacer un JOIN
            "allocated": alloc,
            "spent": spent,
            "percentage": round(pct, 1),
            "status": status
        })
        
    return res

def _mock_budget_status():
    """Generates mock data for frontend testing purposes."""
    return [
        {"id": 1, "category_id": 1, "category_name": "Vivienda & Alquiler", "allocated": 500000, "spent": 400000, "percentage": 80.0, "status": "warning"},
        {"id": 2, "category_id": 2, "category_name": "Supermercado", "allocated": 250000, "spent": 280000, "percentage": 112.0, "status": "overbudget"},
        {"id": 3, "category_id": 3, "category_name": "Transporte / Auto", "allocated": 100000, "spent": 45000, "percentage": 45.0, "status": "ontrack"},
        {"id": 4, "category_id": 4, "category_name": "Ocio & Salidas", "allocated": 150000, "spent": 140000, "percentage": 93.3, "status": "warning"}
    ]
