from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func
from ...dependencies import get_db
from ...models import Account, AccountType
from ...models import TransactionSplit
from ...core.ledger_engine import LedgerEngine
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

router = APIRouter()

# Schemas
class AccountCreate(BaseModel):
    name: str
    type: AccountType
    currency_code: str
    initial_balance: Decimal = Decimal('0')
    notes: Optional[str] = None
    institution_id: Optional[int] = None
    parent_id: Optional[int] = None

class AccountResponse(AccountCreate):
    id: int
    current_balance: Decimal
    is_active: bool

@router.get("/", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    # In production, filter by user_id
    accounts = db.exec(select(Account).where(Account.deleted_at == None)).all()
    return accounts

@router.post("/", response_model=AccountResponse)
def create_account(account_in: AccountCreate, db: Session = Depends(get_db)):
    account = Account(
        **account_in.model_dump(),
        user_id=1, # Mock user
        current_balance=account_in.initial_balance
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@router.get("/{id}", response_model=AccountResponse)
def get_account(id: int, db: Session = Depends(get_db)):
    account = db.get(Account, id)
    if not account or account.deleted_at:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.get("/{id}/balance")
def get_account_balance(id: int, db: Session = Depends(get_db)):
    engine = LedgerEngine(db)
    balance = engine.get_account_balance(id)
    return {"account_id": id, "balance": balance}

@router.get("/{id}/transactions")
def get_account_ledger(id: int, skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    engine = LedgerEngine(db)
    register = engine.get_account_register(id, limit, skip)
    # Re-map for simpler frontend consumption
    result = []
    for tx, split in register:
        result.append({
            "id": tx.id,
            "date": tx.date,
            "description": tx.description,
            "amount": split.amount,
            "reconciled": split.reconciled,
            "status": tx.status
        })
    return result

@router.put("/{id}", response_model=AccountResponse)
def update_account(id: int, account_in: AccountCreate, db: Session = Depends(get_db)):
    account = db.get(Account, id)
    if not account or account.deleted_at:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    update_data = account_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(account, key, value)
        
    db.add(account)
    db.commit()
    db.refresh(account)
    return account

@router.delete("/{id}", response_model=dict)
def delete_account(id: int, db: Session = Depends(get_db)):
    account = db.get(Account, id)
    if not account or account.deleted_at:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    # Soft delete
    account.deleted_at = datetime.utcnow()
    db.add(account)
    db.commit()
    return {"status": "success", "message": "Cuenta eliminada correctamente"}

class ReconcileRequest(BaseModel):
    statement_balance: Decimal
    statement_date: datetime

@router.post("/{id}/reconcile")
async def reconcile_account(id: int, req: ReconcileRequest, db: Session = Depends(get_db)):
    """
    Concilia la cuenta basándose en un saldo de extracto y una fecha de corte.
    Si el saldo calculado internamente coincide, marca como reconciliadas las transacciones.
    """
    account = db.get(Account, id)
    if not account or account.deleted_at:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    engine = LedgerEngine(db)
    try:
        await engine.reconcile_account(id, req.statement_balance, req.statement_date)
        return {"status": "success", "message": "Cuenta conciliada correctamente."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/summary/")
def get_accounts_summary(db: Session = Depends(get_db)):
    """Aggregated info of all accounts."""
    # Group by currency for consolidation
    # This is a simple mock-up of the logic
    return {
        "total_assets": 1500000.00,
        "total_liabilities": 250000.00,
        "net_worth": 1250000.00
    }

