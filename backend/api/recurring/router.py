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

from backend.core.recurring_service import recurring_service
from ..base_crud import BaseCRUDService
from ..schemas.common import PaginatedResponse

router = APIRouter(prefix="/recurring", tags=["Recurring Transactions"])

# Initialize generic service
recurring_crud = BaseCRUDService[TransaccionRecurrente, TransaccionRecurrenteCreate, TransaccionRecurrenteUpdate](TransaccionRecurrente)

@router.get("/", response_model=PaginatedResponse[TransaccionRecurrenteResponse])
def list_recurring(
    offset: int = 0,
    limit: int = 100,
    activo: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """List all recurring transactions with pagination"""
    filters = {}
    if activo is not None:
        filters["activo"] = activo
    
    return recurring_crud.list(session, offset, limit, filters=filters)

@router.post("/", response_model=TransaccionRecurrenteResponse, status_code=status.HTTP_201_CREATED)
def create_recurring(
    data: TransaccionRecurrenteCreate,
    session: Session = Depends(get_session)
):
    """Create a new recurring transaction schedule"""
    return recurring_crud.create(session, data)

@router.get("/{id_recurrencia}", response_model=TransaccionRecurrenteResponse)
def get_recurring(id_recurrencia: int, session: Session = Depends(get_session)):
    """Get details of a specific recurring schedule"""
    recurring = recurring_crud.get(session, id_recurrencia)
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
    recurring = recurring_crud.get(session, id_recurrencia)
    if not recurring:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    
    return recurring_crud.update(session, recurring, data)

@router.delete("/{id_recurrencia}", status_code=status.HTTP_204_NO_CONTENT)
def delete_recurring(id_recurrencia: int, session: Session = Depends(get_session)):
    """Delete a recurring schedule"""
    success = recurring_crud.delete(session, id_recurrencia)
    if not success:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
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
