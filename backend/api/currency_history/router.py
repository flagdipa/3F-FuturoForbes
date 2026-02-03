"""
API Router for Currency History (Historial Divisas)
Provides historical exchange rates and currency conversion
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from sqlmodel import Session, select
from typing import List, Optional
from datetime import date, datetime
from decimal import Decimal
from backend.core.database import get_session
from backend.models.models_extended import HistorialDivisa
from .schemas import (
    HistorialDivisaCreate, HistorialDivisaUpdate, HistorialDivisaResponse,
    ConversionRequest, ConversionResponse
)

router = APIRouter(prefix="/currency-history", tags=["Currency History"])


# ==================== CURRENCY HISTORY CRUD ====================

@router.get("/{id_divisa}", response_model=List[HistorialDivisaResponse])
def get_currency_history(
    id_divisa: int,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    session: Session = Depends(get_session)
):
    """Get historical exchange rates for a currency"""
    query = select(HistorialDivisa).where(HistorialDivisa.id_divisa == id_divisa)
    
    if fecha_desde:
        query = query.where(HistorialDivisa.fecha_tasa >= fecha_desde)
    if fecha_hasta:
        query = query.where(HistorialDivisa.fecha_tasa <= fecha_hasta)
    
    query = query.order_by(HistorialDivisa.fecha_tasa.desc())
    
    history = session.exec(query).all()
    return history


@router.get("/{id_divisa}/rate", response_model=HistorialDivisaResponse)
def get_rate_for_date(
    id_divisa: int,
    fecha: date = Query(..., description="Fecha para obtener la tasa"),
    session: Session = Depends(get_session)
):
    """Get exchange rate for a specific date (or closest previous date)"""
    # Try exact date first
    rate = session.exec(
        select(HistorialDivisa).where(
            HistorialDivisa.id_divisa == id_divisa,
            HistorialDivisa.fecha_tasa == fecha
        )
    ).first()
    
    if rate:
        return rate
    
    # Find closest previous date
    rate = session.exec(
        select(HistorialDivisa)
        .where(
            HistorialDivisa.id_divisa == id_divisa,
            HistorialDivisa.fecha_tasa < fecha
        )
        .order_by(HistorialDivisa.fecha_tasa.desc())
        .limit(1)
    ).first()
    
    if not rate:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró tasa para la divisa {id_divisa} en o antes de {fecha}"
        )
    
    return rate


@router.post("/", response_model=HistorialDivisaResponse, status_code=status.HTTP_201_CREATED)
def add_currency_rate(
    rate_data: HistorialDivisaCreate,
    session: Session = Depends(get_session)
):
    """Add a new exchange rate"""
    # Check for duplicate
    existing = session.exec(
        select(HistorialDivisa).where(
            HistorialDivisa.id_divisa == rate_data.id_divisa,
            HistorialDivisa.fecha_tasa == rate_data.fecha_tasa
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe una tasa para esta divisa en la fecha {rate_data.fecha_tasa}"
        )
    
    rate = HistorialDivisa(**rate_data.dict())
    session.add(rate)
    session.commit()
    session.refresh(rate)
    return rate


@router.put("/{id_historial}", response_model=HistorialDivisaResponse)
def update_currency_rate(
    id_historial: int,
    rate_data: HistorialDivisaUpdate,
    session: Session = Depends(get_session)
):
    """Update an existing exchange rate"""
    rate = session.get(HistorialDivisa, id_historial)
    if not rate:
        raise HTTPException(status_code=404, detail="Registro de tasa no encontrado")
    
    for key, value in rate_data.dict(exclude_unset=True).items():
        setattr(rate, key, value)
    
    session.add(rate)
    session.commit()
    session.refresh(rate)
    return rate


@router.delete("/{id_historial}", status_code=status.HTTP_204_NO_CONTENT)
def delete_currency_rate(id_historial: int, session: Session = Depends(get_session)):
    """Delete an exchange rate"""
    rate = session.get(HistorialDivisa, id_historial)
    if not rate:
        raise HTTPException(status_code=404, detail="Registro de tasa no encontrado")
    
    session.delete(rate)
    session.commit()
    return None


# ==================== CURRENCY CONVERSION ====================

@router.post("/convert", response_model=ConversionResponse)
def convert_currency(
    conversion: ConversionRequest,
    session: Session = Depends(get_session)
):
    """Convert amount between currencies using historical rate"""
    
    # Get rate for source currency
    rate_origen = session.exec(
        select(HistorialDivisa)
        .where(
            HistorialDivisa.id_divisa == conversion.id_divisa_origen,
            HistorialDivisa.fecha_tasa <= conversion.fecha
        )
        .order_by(HistorialDivisa.fecha_tasa.desc())
        .limit(1)
    ).first()
    
    # Get rate for destination currency
    rate_destino = session.exec(
        select(HistorialDivisa)
        .where(
            HistorialDivisa.id_divisa == conversion.id_divisa_destino,
            HistorialDivisa.fecha_tasa <= conversion.fecha
        )
        .order_by(HistorialDivisa.fecha_tasa.desc())
        .limit(1)
    ).first()
    
    if not rate_origen or not rate_destino:
        raise HTTPException(
            status_code=404,
            detail="No se encontraron tasas para una o ambas divisas"
        )
    
    # Convert: amount * (rate_destino / rate_origen)
    tasa_conversion = rate_destino.tasa_valor / rate_origen.tasa_valor
    monto_convertido = conversion.monto * tasa_conversion
    
    return ConversionResponse(
        monto_original=conversion.monto,
        monto_convertido=monto_convertido,
        tasa_utilizada=tasa_conversion,
        fecha_tasa=max(rate_origen.fecha_tasa, rate_destino.fecha_tasa)
    )
