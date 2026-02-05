"""
API Router for Recurring Transactions (Transacciones Programadas)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from backend.core.database import get_session
from backend.models.models_advanced import TransaccionRecurrente
from backend.models.models import LibroTransacciones
from .schemas import (
    TransaccionRecurrenteCreate, TransaccionRecurrenteUpdate, 
    TransaccionRecurrenteResponse
)
from backend.core.recurring_service import recurring_service

router = APIRouter(prefix="/recurring", tags=["Recurring Transactions"])

@router.get("/", response_model=List[TransaccionRecurrenteResponse])
def list_recurring(
    activo: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """List all recurring transactions"""
    query = select(TransaccionRecurrente)
    if activo is not None:
        query = query.where(TransaccionRecurrente.activo == activo)
    
    results = session.exec(query).all()
    return results

@router.post("/", response_model=TransaccionRecurrenteResponse, status_code=status.HTTP_201_CREATED)
def create_recurring(
    data: TransaccionRecurrenteCreate,
    session: Session = Depends(get_session)
):
    """Create a new recurring transaction schedule"""
    recurring = TransaccionRecurrente(**data.dict())
    session.add(recurring)
    session.commit()
    session.refresh(recurring)
    return recurring

@router.get("/{id_recurrencia}", response_model=TransaccionRecurrenteResponse)
def get_recurring(id_recurrencia: int, session: Session = Depends(get_session)):
    """Get details of a specific recurring schedule"""
    recurring = session.get(TransaccionRecurrente, id_recurrencia)
    if not recurring:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    return recurring

@router.put("/{id_recurrencia}", response_model=TransaccionRecurrenteResponse)
def update_recurring(
    id_recurrencia: int,
    data: TransaccionRecurrenteUpdate,
    session: Session = Depends(get_session)
):
    """Update a recurring schedule"""
    recurring = session.get(TransaccionRecurrente, id_recurrencia)
    if not recurring:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(recurring, key, value)
    
    session.add(recurring)
    session.commit()
    session.refresh(recurring)
    return recurring

@router.delete("/{id_recurrencia}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring(id_recurrencia: int, session: Session = Depends(get_session)):
    """Delete a recurring schedule"""
    recurring = session.get(TransaccionRecurrente, id_recurrencia)
    if not recurring:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    
    session.delete(recurring)
    session.commit()
    return None

@router.post("/{id_recurrencia}/execute", response_model=LibroTransacciones)
def execute_recurring_manual(
    id_recurrencia: int,
    session: Session = Depends(get_session)
):
    """Manually execute a recurring transaction now"""
    try:
        # recurring_service must be imported. It is imported as 'recurring_service' on line 16.
        result = recurring_service.execute_recurring(session, id_recurrencia)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")
