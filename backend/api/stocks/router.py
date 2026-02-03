"""
API Router for Investments (Inversiones / Stocks)
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import date
from backend.core.database import get_session
from backend.models.models_advanced import Inversion, HistorialInversion
from .schemas import (
    InversionCreate, InversionUpdate, InversionResponse,
    HistorialInversionCreate, HistorialInversionResponse,
    PortfolioSummary
)

router = APIRouter(prefix="/stocks", tags=["Investments"])

# ==================== INVESTMENTS CRUD ====================

@router.get("/", response_model=List[InversionResponse])
def list_investments(
    activo: Optional[int] = None,
    id_cuenta: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """List all stock holdings"""
    query = select(Inversion)
    if activo is not None:
        query = query.where(Inversion.activo == activo)
    if id_cuenta is not None:
        query = query.where(Inversion.id_cuenta == id_cuenta)
    
    results = session.exec(query).all()
    return results

@router.post("/", response_model=InversionResponse, status_code=status.HTTP_201_CREATED)
def create_investment(data: InversionCreate, session: Session = Depends(get_session)):
    """Add a new stock holding"""
    investment = Inversion(**data.dict())
    session.add(investment)
    session.commit()
    session.refresh(investment)
    
    # Create initial history entry
    history = HistorialInversion(
        id_inversion=investment.id_inversion,
        fecha=date.today(),
        precio=investment.precio_actual
    )
    session.add(history)
    session.commit()
    
    return investment

@router.get("/summary", response_model=PortfolioSummary)
def get_portfolio_summary(session: Session = Depends(get_session)):
    """Calculate total portfolio performance"""
    investments = session.exec(select(Inversion).where(Inversion.activo == 1)).all()
    
    total_invested = sum(i.cantidad * i.precio_compra + i.comision for i in investments)
    current_value = sum(i.cantidad * i.precio_actual for i in investments)
    
    profit_loss = current_value - total_invested
    percentage = (profit_loss / total_invested * 100) if total_invested > 0 else 0
    
    return {
        "total_invested": total_invested,
        "current_value": current_value,
        "total_profit_loss": profit_loss,
        "profit_loss_percentage": percentage
    }

@router.get("/{id_inversion}", response_model=InversionResponse)
def get_investment(id_inversion: int, session: Session = Depends(get_session)):
    """Get details for a specific holding"""
    investment = session.get(Inversion, id_inversion)
    if not investment:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    return investment

@router.put("/{id_inversion}", response_model=InversionResponse)
def update_investment(
    id_inversion: int,
    data: InversionUpdate,
    session: Session = Depends(get_session)
):
    """Update investment details or current market price"""
    investment = session.get(Inversion, id_inversion)
    if not investment:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    
    # If price is updated, record in history
    if data.precio_actual is not None and data.precio_actual != investment.precio_actual:
        history = HistorialInversion(
            id_inversion=investment.id_inversion,
            fecha=date.today(),
            precio=data.precio_actual
        )
        session.add(history)
    
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(investment, key, value)
    
    session.add(investment)
    session.commit()
    session.refresh(investment)
    return investment

@router.delete("/{id_inversion}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(id_inversion: int, session: Session = Depends(get_session)):
    """Remove an investment holding and history"""
    investment = session.get(Inversion, id_inversion)
    if not investment:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    
    session.delete(investment)
    session.commit()
    return None

# ==================== PRICE HISTORY ====================

@router.get("/{id_inversion}/history", response_model=List[HistorialInversionResponse])
def get_investment_history(id_inversion: int, session: Session = Depends(get_session)):
    """Get price history for a holding"""
    # Verify investment exists
    inv = session.get(Inversion, id_inversion)
    if not inv:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
        
    query = select(HistorialInversion).where(HistorialInversion.id_inversion == id_inversion).order_by(HistorialInversion.fecha.desc())
    results = session.exec(query).all()
    return results

@router.post("/history", response_model=HistorialInversionResponse, status_code=status.HTTP_201_CREATED)
def add_price_entry(data: HistorialInversionCreate, session: Session = Depends(get_session)):
    """Add a historical price point"""
    # Verify investment exists
    inv = session.get(Inversion, data.id_inversion)
    if not inv:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
        
    history = HistorialInversion(**data.dict())
    session.add(history)
    
    # Update current market price in investment
    inv.precio_actual = data.precio
    session.add(inv)
    
    session.commit()
    session.refresh(history)
    return history
