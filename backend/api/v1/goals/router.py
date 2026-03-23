from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime

from ....dependencies import get_db
from ....models import SavingGoal, GoalContribution, User
from ...auth.deps import get_current_user

router = APIRouter()

# --- Schemas ---
class GoalCreate(BaseModel):
    name: str
    target_amount: Decimal
    target_date: Optional[date] = None
    currency_code: str
    current_amount: Decimal = Decimal('0')
    account_id: Optional[int] = None
    color: str = "#0d6efd"
    icon: str = "fa-bullseye"
    notes: Optional[str] = None

class GoalUpdate(BaseModel):
    name: Optional[str] = None
    target_amount: Optional[Decimal] = None
    target_date: Optional[date] = None
    currency_code: Optional[str] = None
    current_amount: Optional[Decimal] = None
    is_completed: Optional[bool] = None
    account_id: Optional[int] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class GoalResponse(GoalCreate):
    id: int
    is_completed: bool
    created_at: datetime
    progress_percentage: float
    status: str
    account_id: Optional[int] = None
    color: str
    icon: str
    notes: Optional[str] = None
    
class ContributionCreate(BaseModel):
    amount: Decimal
    transaction_id: Optional[int] = None

# --- Endpoints ---
@router.get("/", response_model=List[GoalResponse])
def list_goals(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """Lista todas las metas de ahorro con su progreso calculado"""
    goals = db.exec(
        select(SavingGoal).where(
            SavingGoal.deleted_at == None,
            SavingGoal.user_id == current_user.id
        )
    ).all()
        
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

@router.post("/", response_model=GoalResponse, status_code=201)
def create_goal(
    goal_in: GoalCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea una nueva meta de ahorro"""
    goal = SavingGoal(
        user_id=current_user.id,
        name=goal_in.name,
        target_amount=goal_in.target_amount,
        target_date=goal_in.target_date,
        currency_code=goal_in.currency_code,
        current_amount=goal_in.current_amount,
        account_id=goal_in.account_id,
        color=goal_in.color,
        icon=goal_in.icon,
        notes=goal_in.notes
    )
    # Autocomplete if initial amount >= target
    if goal.current_amount >= goal.target_amount:
        goal.is_completed = True
        
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    # Compute fields for response
    g_dict = goal.model_dump()
    g_dict["progress_percentage"] = float((goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0
    g_dict["status"] = "ontrack"
    return g_dict

@router.patch("/{id}", response_model=GoalResponse)
def update_goal(
    id: int, 
    goal_in: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Actualiza una meta de ahorro"""
    goal = db.get(SavingGoal, id)
    if not goal or goal.deleted_at or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meta no encontrada")
        
    for key, value in goal_in.model_dump(exclude_unset=True).items():
        setattr(goal, key, value)
        
    # Recalculate completion
    if goal.current_amount >= goal.target_amount:
        goal.is_completed = True
    else:
        goal.is_completed = False
        
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    # Compute fields for response
    g_dict = goal.model_dump()
    pct = float((goal.current_amount / goal.target_amount) * 100) if goal.target_amount > 0 else 0
    g_dict["progress_percentage"] = round(pct, 1)
    g_dict["status"] = "ontrack" # Simplification
    return g_dict

@router.post("/{id}/contribute")
def add_contribution(
    id: int, 
    cont: ContributionCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Añade fondos a una meta de ahorro existente"""
    goal = db.get(SavingGoal, id)
    if not goal or goal.deleted_at or goal.user_id != current_user.id:
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
def delete_goal(
    id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft-delete de una meta"""
    goal = db.get(SavingGoal, id)
    if not goal or goal.deleted_at or goal.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Meta de ahorro no encontrada")
        
    goal.deleted_at = datetime.utcnow()
    db.add(goal)
    db.commit()
    return {"message": "Meta eliminada correctamente"}
