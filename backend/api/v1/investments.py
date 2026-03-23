from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlmodel import Session
from sqlmodel import select, desc
from datetime import datetime
from decimal import Decimal
import logging

from ...dependencies import get_db
from ...models import Investment, InvestmentPrice, InvestmentTransaction, User
from ..auth.deps import get_current_user

logger = logging.getLogger("api_investments")
router = APIRouter()

# Schemas
from pydantic import BaseModel

class InvestmentCreate(BaseModel):
    symbol: str
    name: str
    type: str # STOCK, ETF, CRYPTO, etc.
    currency_code: str
    notes: Optional[str] = None

class InvestmentResponse(InvestmentCreate):
    id: int
    created_at: datetime

class InvestmentTransactionCreate(BaseModel):
    account_id: int # Origen de los fondos
    date: datetime
    type: str # BUY, SELL
    quantity: Decimal
    price_per_unit: Decimal
    commission: Decimal = Decimal('0')
    taxes: Decimal = Decimal('0')
    notes: Optional[str] = None

@router.get("/", response_model=List[InvestmentResponse])
def get_portfolio(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    investments = db.exec(select(Investment).where(Investment.deleted_at == None, Investment.user_id == current_user.id)).all()
    return investments

@router.post("/", response_model=InvestmentResponse)
def create_investment(inv_in: InvestmentCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    investment = Investment(**inv_in.model_dump(), user_id=current_user.id)
    db.add(investment)
    db.commit()
    db.refresh(investment)
    return investment

@router.post("/{id}/transactions")
def add_transaction(id: int, tx_in: InvestmentTransactionCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    investment = db.get(Investment, id)
    if not investment or investment.deleted_at or investment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
        
    total_amount = (tx_in.quantity * tx_in.price_per_unit) + tx_in.commission + tx_in.taxes
    
    # In a real scenario, this should also deduct/add money from the associated `account_id` via LedgerEngine
    transaction = InvestmentTransaction(
        **tx_in.model_dump(),
        investment_id=id,
        user_id=current_user.id,
        total_amount=total_amount
    )
    db.add(transaction)
    
    # Add a price snapshot as well to reflect the actual paid price
    price_snapshot = InvestmentPrice(
        investment_id=id,
        price=tx_in.price_per_unit,
        source="TRANSACTION"
    )
    db.add(price_snapshot)
    
    db.commit()
    return {"message": "Transacción registrada con éxito", "total_amount": float(total_amount)}

@router.get("/{id}/history")
def get_price_history(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    investment = db.get(Investment, id)
    if not investment or investment.deleted_at or investment.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Inversión no encontrada")
        
    prices = db.exec(
        select(InvestmentPrice)
        .where(InvestmentPrice.investment_id == id)
        .order_by(desc(InvestmentPrice.price_date))
        .limit(100)
    ).all()
    return [{"date": p.price_date, "price": float(p.price)} for p in prices]

@router.get("/performance")
def get_portfolio_performance(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Calcula rendimientos, P&L general, allocation y valuación"""
    # Pseudo-lógica para demostrar el concepto del dashboard:
    # 1. Obtener todas las posiciones de un usuario y sumar compras vs actual valuation
    return {
        "status": "success",
        "total_value": 850000.00,
        "invested_capital": 750000.00,
        "unrealized_pnl": 100000.00,
        "unrealized_pnl_pct": 13.33,
        "allocation": [
            {"type": "STOCK", "percentage": 45, "value": 382500},
            {"type": "CRYPTO", "percentage": 25, "value": 212500},
            {"type": "ETF", "percentage": 30, "value": 255000}
        ]
    }
