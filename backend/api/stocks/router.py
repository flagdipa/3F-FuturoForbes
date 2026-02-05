"""
API Router for Investments (Inversiones / Stocks)
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from sqlmodel import Session, select, func
from typing import List, Optional
from datetime import date
from backend.core.database import get_session
from backend.models.models_advanced import Inversion, HistorialInversion
from backend.models.models import Usuario
from ..auth.deps import get_current_user
from ..base_crud import BaseCRUDService
from ..schemas.common import PaginatedResponse
from .schemas import (
    InversionCreate, InversionUpdate, InversionResponse,
    HistorialInversionCreate, HistorialInversionResponse,
    PortfolioSummary
)

router = APIRouter(prefix="/stocks", tags=["Investments"])
stock_service = BaseCRUDService[Inversion, InversionCreate, InversionUpdate](Inversion)

# ==================== INVESTMENTS CRUD ====================

@router.get("/", response_model=PaginatedResponse[InversionResponse])
def list_investments(
    offset: int = 0,
    limit: int = 100,
    activo: Optional[int] = None,
    id_cuenta: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """List all stock holdings with pagination"""
    filters = {}
    if activo is not None: filters["activo"] = activo
    if id_cuenta is not None: filters["id_cuenta"] = id_cuenta
    
    return stock_service.list(session, offset=offset, limit=limit, filters=filters)

@router.post("/", response_model=InversionResponse, status_code=status.HTTP_201_CREATED)
def create_investment(
    data: InversionCreate, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Add a new stock holding with audit"""
    investment = stock_service.create(
        session, data, 
        user_id=current_user.id_usuario, 
        ip_address=request.client.host
    )
    
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
    investment = stock_service.get(session, id_inversion)
    if not investment:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    return investment

@router.put("/{id_inversion}", response_model=InversionResponse)
def update_investment(
    id_inversion: int,
    data: InversionUpdate,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Update investment details or current market price with audit"""
    investment = stock_service.get(session, id_inversion)
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
    
    return stock_service.update(
        session, investment, data,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )

@router.delete("/{id_inversion}", status_code=status.HTTP_204_NO_CONTENT)
def delete_investment(
    id_inversion: int, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Remove an investment holding and history with audit"""
    success = stock_service.delete(
        session, id_inversion,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )
    if not success:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
    return None

# ==================== PRICE HISTORY ====================

@router.get("/{id_inversion}/history", response_model=List[HistorialInversionResponse])
def get_investment_history(id_inversion: int, session: Session = Depends(get_session)):
    """Get price history for a holding (kept as simple list for charts)"""
    inv = stock_service.get(session, id_inversion)
    if not inv:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
        
    query = select(HistorialInversion).where(HistorialInversion.id_inversion == id_inversion).order_by(HistorialInversion.fecha.desc())
    results = session.exec(query).all()
    return results

@router.post("/history", response_model=HistorialInversionResponse, status_code=status.HTTP_201_CREATED)
def add_price_entry(
    data: HistorialInversionCreate, 
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Add a historical price point (History is smaller audit, tracked via stock update)"""
    inv = stock_service.get(session, data.id_inversion)
    if not inv:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
        
    history = HistorialInversion(**data.dict())
    session.add(history)
    
    # Update current market price in investment (this triggers audit if using service)
    # But here we do it manually to keep history simple
    inv.precio_actual = data.precio
    session.add(inv)
    
    session.commit()
    session.refresh(history)
    return history
