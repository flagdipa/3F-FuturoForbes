from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List, Optional
from decimal import Decimal
from ...core.database import get_session
from ..auth.deps import get_current_user
from ...models.models import MetaAhorro, Usuario, ListaCuentas, LibroTransacciones
from datetime import datetime

router = APIRouter(prefix="/goals", tags=["Metas"])

def _calculate_account_balance(session: Session, id_cuenta: int) -> Decimal:
    """Calculate the current balance of an account: saldo_inicial + sum(transactions)."""
    account = session.get(ListaCuentas, id_cuenta)
    if not account:
        return Decimal(0)

    result = session.exec(
        select(func.coalesce(func.sum(LibroTransacciones.monto_transaccion), 0))
        .where(LibroTransacciones.id_cuenta == id_cuenta)
        .where(LibroTransacciones.fecha_eliminacion == None)
    ).one()

    return account.saldo_inicial + Decimal(str(result))

def _sync_goal_balance(session: Session, goal: MetaAhorro) -> MetaAhorro:
    """If the goal is linked to an account, update monto_actual from account balance."""
    if goal.id_cuenta:
        balance = _calculate_account_balance(session, goal.id_cuenta)
        goal.monto_actual = balance
        goal.fecha_actualizacion = datetime.utcnow().isoformat()
        session.add(goal)
        session.commit()
        session.refresh(goal)
    return goal

@router.get("/", response_model=List[MetaAhorro])
def read_goals(
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Retrieve all savings goals for the current user. If linked to an account, auto-sync balance."""
    statement = select(MetaAhorro).where(MetaAhorro.id_usuario == current_user.id_usuario)
    goals = session.exec(statement).all()
    
    # Auto-sync goals linked to accounts
    for goal in goals:
        if goal.id_cuenta:
            _sync_goal_balance(session, goal)
    
    return goals

@router.post("/", response_model=MetaAhorro)
def create_goal(
    goal: MetaAhorro,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a new savings goal. Optionally link to an account for auto-tracking."""
    goal.id_usuario = current_user.id_usuario
    goal.fecha_creacion = datetime.utcnow().isoformat()
    goal.fecha_actualizacion = datetime.utcnow().isoformat()
    
    # If linked to account, set initial monto_actual from account balance
    if goal.id_cuenta:
        goal.monto_actual = _calculate_account_balance(session, goal.id_cuenta)
    
    session.add(goal)
    session.commit()
    session.refresh(goal)
    return goal

@router.put("/{goal_id}", response_model=MetaAhorro)
def update_goal(
    goal_id: int,
    goal_update: MetaAhorro,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Update a savings goal."""
    db_goal = session.get(MetaAhorro, goal_id)
    if not db_goal or db_goal.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=404, detail="Meta not found")
    
    goal_data = goal_update.dict(exclude_unset=True)
    goal_data.pop("id_meta", None)
    goal_data.pop("id_usuario", None)
    
    for key, value in goal_data.items():
        setattr(db_goal, key, value)
        
    db_goal.fecha_actualizacion = datetime.utcnow().isoformat()
    
    # Recalculate if linked to account
    if db_goal.id_cuenta:
        db_goal.monto_actual = _calculate_account_balance(session, db_goal.id_cuenta)
    
    session.add(db_goal)
    session.commit()
    session.refresh(db_goal)
    return db_goal

@router.delete("/{goal_id}")
def delete_goal(
    goal_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Delete a savings goal."""
    db_goal = session.get(MetaAhorro, goal_id)
    if not db_goal or db_goal.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=404, detail="Meta not found")
        
    session.delete(db_goal)
    session.commit()
    return {"ok": True}

@router.post("/{goal_id}/recalculate", response_model=MetaAhorro)
def recalculate_goal(
    goal_id: int,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Force recalculate the current amount of a goal from its linked account balance."""
    db_goal = session.get(MetaAhorro, goal_id)
    if not db_goal or db_goal.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=404, detail="Meta not found")
    
    if not db_goal.id_cuenta:
        raise HTTPException(
            status_code=400, 
            detail="Esta meta no está vinculada a ninguna cuenta"
        )
    
    _sync_goal_balance(session, db_goal)
    return db_goal
