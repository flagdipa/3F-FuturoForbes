from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime

from ....dependencies import get_db
from ....models import SavingGoal, GoalContribution

router = APIRouter()

# --- Schemas ---
class GoalCreate(BaseModel):
    name: str
    target_amount: Decimal
    target_date: Optional[date] = None
    currency_code: str
    current_amount: Decimal = Decimal('0')

class GoalResponse(GoalCreate):
    id: int
    is_completed: bool
    created_at: datetime
    progress_percentage: float
    status: str # "ontrack", "delayed"
    
class ContributionCreate(BaseModel):
    amount: Decimal
    transaction_id: Optional[int] = None

# --- Endpoints ---
@router.get("/", response_model=List[GoalResponse])
def list_goals(db: Session = Depends(get_db)):
    """Lista todas las metas de ahorro con su progreso calculado"""
    goals = db.exec(select(SavingGoal).where(SavingGoal.deleted_at == None)).all()
    
    # Mock data for frontend rendering if DB is empty
    if not goals:
        return [
            {
                "id": 1,
                "name": "Fondo de Emergencia",
                "target_amount": Decimal('10000'),
                "current_amount": Decimal('4500'),
                "target_date": date(2025, 12, 31),
                "currency_code": "USD",
                "is_completed": False,
                "created_at": datetime.utcnow(),
                "progress_percentage": 45.0,
                "status": "ontrack"
            },
            {
                "id": 2,
                "name": "Vacaciones Japón",
                "target_amount": Decimal('5000000'),
                "current_amount": Decimal('1200000'),
                "target_date": date(2026, 8, 15),
                "currency_code": "ARS",
                "is_completed": False,
                "created_at": datetime.utcnow(),
                "progress_percentage": 24.0,
                "status": "delayed"
            }
        ]
        
    res = []
    for g in goals:
        pct = float((g.current_amount / g.target_amount) * 100) if g.target_amount > 0 else 0
        
        # Simple status logic based on time elapsed vs progress
        status = "ontrack"
        if g.target_date:
            days_total = (g.target_date - g.created_at.date()).days
            days_elapsed = (date.today() - g.created_at.date()).days
            if days_total > 0:
                time_pct = (days_elapsed / days_total) * 100
                if time_pct > pct + 10: # Si gastaste 10% más de tiempo de lo que llevas ahorrado 
                    status = "delayed"
                    
        g_dict = g.model_dump()
        g_dict["progress_percentage"] = round(pct, 1)
        g_dict["status"] = status
        res.append(g_dict)
        
    return res

@router.post("/", response_model=GoalResponse)
def create_goal(goal_in: GoalCreate, db: Session = Depends(get_db)):
    """Crea una nueva meta de ahorro"""
    goal = SavingGoal(
        user_id=1, # Mock User
        name=goal_in.name,
        target_amount=goal_in.target_amount,
        target_date=goal_in.target_date,
        currency_code=goal_in.currency_code,
        current_amount=goal_in.current_amount
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    # Dummy attach fields for response
    g_dict = goal.model_dump()
    g_dict["progress_percentage"] = float((goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0
    g_dict["status"] = "ontrack"
    return g_dict

@router.post("/{id}/contribute")
def add_contribution(id: int, cont: ContributionCreate, db: Session = Depends(get_db)):
    """Añade fondos a una meta de ahorro existente"""
    goal = db.get(SavingGoal, id)
    if not goal or goal.deleted_at:
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")
        
    goal.current_amount += cont.amount
    if goal.current_amount >= goal.target_amount:
        goal.is_completed = True
        
    contribution = GoalContribution(
        goal_id=goal.id,
        amount=cont.amount,
        transaction_id=cont.transaction_id
    )
    
    db.add(contribution)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    return {"message": "Contribución registrada exitosamente", "current_amount": goal.current_amount}

@router.delete("/{id}")
def delete_goal(id: int, db: Session = Depends(get_db)):
    """Soft-delete de una meta"""
    goal = db.get(SavingGoal, id)
    if not goal or goal.deleted_at:
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")
        
    goal.deleted_at = datetime.utcnow()
    db.add(goal)
    db.commit()
    return {"message": "Meta eliminada correctamente"}
