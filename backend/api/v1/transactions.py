from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from ...dependencies import get_db
from ...core.ledger_engine import LedgerEngine, LedgerError
from .schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate, TransferCreate
from ...models import Transaction

router = APIRouter()

# Mock user for development
CURRENT_USER_ID = 1

@router.post("/", response_model=TransactionResponse)
async def create_transaction(
    tx_in: TransactionCreate, 
    db: Session = Depends(get_db)
):
    engine = LedgerEngine(db)
    try:
        splits_data = [s.model_dump() for s in tx_in.splits]
        transaction = await engine.create_transaction(
            user_id=CURRENT_USER_ID,
            date=tx_in.date,
            description=tx_in.description,
            splits=splits_data,
            payee_id=tx_in.payee_id,
            reference_number=tx_in.reference_number,
            notes=tx_in.notes
        )
        return transaction
    except LedgerError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    transactions = db.query(Transaction).offset(skip).limit(limit).all()
    return transactions

@router.get("/{id}", response_model=TransactionResponse)
def get_transaction(id: int, db: Session = Depends(get_db)):
    transaction = db.query(Transaction).filter(Transaction.id == id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.post("/{id}/void", response_model=TransactionResponse)
async def void_transaction(id: int, reason: str = "", db: Session = Depends(get_db)):
    engine = LedgerEngine(db)
    try:
        transaction = await engine.void_transaction(id, reason)
        return transaction
    except LedgerError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/transfer", response_model=TransactionResponse)
async def create_transfer(
    transfer_in: TransferCreate,
    db: Session = Depends(get_db)
):
    """Convenience helper to create a symmetric transfer between two accounts."""
    engine = LedgerEngine(db)
    
    # Define the two halves of the transfer
    splits = [
        {
            "account_id": transfer_in.from_account_id,
            "amount": -transfer_in.amount, # Credit (Out)
            "currency_code": transfer_in.currency_code
        },
        {
            "account_id": transfer_in.to_account_id,
            "amount": transfer_in.amount, # Debit (In)
            "currency_code": transfer_in.currency_code
        }
    ]
    
    try:
        transaction = await engine.create_transaction(
            user_id=CURRENT_USER_ID,
            date=transfer_in.date,
            description=transfer_in.description or f"Transfer from {transfer_in.from_account_id} to {transfer_in.to_account_id}",
            splits=splits
        )
        return transaction
    except LedgerError as e:
        raise HTTPException(status_code=400, detail=str(e))
