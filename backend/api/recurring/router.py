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

def calculate_next_date(current_date: date, frequency: str, interval: int) -> date:
    """Helper to calculate next execution date based on frequency"""
    freq = frequency.lower()
    if freq == "daily":
        return current_date + timedelta(days=interval)
    elif freq == "weekly":
        return current_date + timedelta(weeks=interval)
    elif freq == "monthly":
        return current_date + relativedelta(months=interval)
    elif freq == "yearly":
        return current_date + relativedelta(years=interval)
    return current_date

@router.post("/{id_recurrencia}/execute", response_model=dict)
def execute_recurring(id_recurrencia: int, session: Session = Depends(get_session)):
    """
    Manually trigger execution of a scheduled transaction.
    Creates a real transaction in 'libro_transacciones' and updates next date.
    """
    recurring = session.get(TransaccionRecurrente, id_recurrencia)
    if not recurring:
        raise HTTPException(status_code=404, detail="Programación no encontrada")
    
    if recurring.activo == 0:
        raise HTTPException(status_code=400, detail="La programación está inactiva")

    # 1. Create the real transaction
    transaction = LibroTransacciones(
        id_cuenta=recurring.id_cuenta,
        id_cuenta_destino=recurring.id_cuenta_destino,
        id_beneficiario=recurring.id_beneficiario,
        codigo_transaccion=recurring.codigo_transaccion,
        monto_transaccion=recurring.monto_transaccion,
        id_categoria=recurring.id_categoria,
        notas=f"[Recurrente] {recurring.notas or ''}",
        fecha_transaccion=str(recurring.proxima_fecha)
    )
    session.add(transaction)
    
    # 2. Update recurring schedule
    recurring.ejecuciones_realizadas += 1
    
    # Calculate next proxima_fecha
    recurring.proxima_fecha = calculate_next_date(
        recurring.proxima_fecha, 
        recurring.frecuencia, 
        recurring.intervalo
    )
    
    # Check limits
    if recurring.limite_ejecuciones != -1 and recurring.ejecuciones_realizadas >= recurring.limite_ejecuciones:
        recurring.activo = 0
        
    if recurring.fecha_fin and recurring.proxima_fecha > recurring.fecha_fin:
        recurring.activo = 0
        
    session.add(recurring)
    session.commit()
    
    return {
        "status": "success", 
        "transaction_id": transaction.id_transaccion,
        "next_date": str(recurring.proxima_fecha)
    }
