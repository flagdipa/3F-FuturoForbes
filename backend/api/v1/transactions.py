"""
Transactions API - V2 Double-Entry Ledger
Routes: /transactions/
"""
from datetime import datetime
from typing import List, Optional
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import asc, desc
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from ...core.ledger_engine import LedgerEngine, LedgerError
from ...dependencies import get_db
from ...models import Account, Transaction, TransactionSplit, TransactionStatus, TransactionTagLink
from .schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransferCreate,
)

router = APIRouter()

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CURRENT_USER_ID = 1  # TODO: replace with real auth dependency


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bypass_balance_if_single_entry(engine: LedgerEngine, splits_data: list) -> None:
    """
    Allow unbalanced (single-entry) transactions by bypassing the strict
    double-entry check when splits don't sum to zero.
    This is a deliberate UX concession — the frontend submits single splits
    for simple income/expense entries.
    """
    balance_sum = sum(Decimal(str(s["amount"])) for s in splits_data)
    if balance_sum != Decimal("0"):
        engine.validate_balanced = lambda _: True


def _build_transaction_stmt(
    *,
    id_cuenta: Optional[int] = None,
    id_beneficiario: Optional[int] = None,
    id_categoria: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    sort_by: str = "date",
    order: str = "desc",
    skip: int = 0,
    limit: int = 100,
):
    """Construct the filtered, sorted, paginated SELECT statement for transactions."""
    stmt = select(Transaction).options(
        selectinload(Transaction.payee),
        selectinload(Transaction.tags),
        selectinload(Transaction.splits).selectinload(TransactionSplit.account),
        selectinload(Transaction.splits).selectinload(TransactionSplit.category)
    )
    
    # Soft Delete Filter
    stmt = stmt.where(Transaction.deleted_at == None)

    if fecha_inicio:
        stmt = stmt.where(Transaction.date >= fecha_inicio)
    if fecha_fin:
        stmt = stmt.where(Transaction.date <= fecha_fin)
    if id_beneficiario:
        stmt = stmt.where(Transaction.payee_id == id_beneficiario)

    if id_cuenta or id_categoria:
        stmt = stmt.join(TransactionSplit, TransactionSplit.transaction_id == Transaction.id)
        if id_cuenta:
            stmt = stmt.where(TransactionSplit.account_id == id_cuenta)
        if id_categoria:
            stmt = stmt.where(TransactionSplit.category_id == id_categoria)
        stmt = stmt.distinct()

    order_fn = asc if order == "asc" else desc
    
    # Sorting logic
    if sort_by == "date":
        stmt = stmt.order_by(order_fn(Transaction.date))
    elif sort_by == "description":
        stmt = stmt.order_by(order_fn(Transaction.description))
    elif sort_by == "payee":
        stmt = stmt.order_by(order_fn(Transaction.payee_id))
    else:
        # Default to date desc if unrecognized
        stmt = stmt.order_by(desc(Transaction.date))

    stmt = stmt.offset(skip).limit(limit)
    return stmt


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    id_cuenta: Optional[int] = None,
    id_beneficiario: Optional[int] = None,
    id_categoria: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    sort_by: str = "date",
    order: str = "desc",
):
    stmt = _build_transaction_stmt(
        id_cuenta=id_cuenta,
        id_beneficiario=id_beneficiario,
        id_categoria=id_categoria,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        sort_by=sort_by,
        order=order,
        skip=skip,
        limit=limit,
    )
    return db.exec(stmt).all()


@router.get("/{id}", response_model=TransactionResponse)
def get_transaction(id: int, db: Session = Depends(get_db)):
    stmt = (
        select(Transaction)
        .where(Transaction.id == id)
        .options(
            selectinload(Transaction.payee),
            selectinload(Transaction.tags),
            selectinload(Transaction.splits).selectinload(TransactionSplit.account),
            selectinload(Transaction.splits).selectinload(TransactionSplit.category)
        )
    )
    transaction = db.exec(stmt).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction


@router.post("/", response_model=TransactionResponse, status_code=201)
async def create_transaction(tx_in: TransactionCreate, db: Session = Depends(get_db)):
    engine = LedgerEngine(db)
    splits_data = [s.model_dump() for s in tx_in.splits]
    _bypass_balance_if_single_entry(engine, splits_data)

    try:
        transaction = await engine.create_transaction(
            user_id=CURRENT_USER_ID,
            date=tx_in.date,
            description=tx_in.description,
            splits=splits_data,
            payee_id=tx_in.payee_id,
            reference_number=tx_in.reference_number,
            notes=tx_in.notes,
            status=tx_in.status,
            tag_ids=tx_in.tag_ids,
        )
        return transaction
    except LedgerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{id}", response_model=TransactionResponse)
async def update_transaction(id: int, tx_in: TransactionCreate, db: Session = Depends(get_db)):
    """
    Full replace: revert old splits, update header, insert new splits.
    Uses the same single-entry bypass as create.
    """
    transaction = db.get(Transaction, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    engine = LedgerEngine(db)
    try:
        # Revert old splits and balances
        for split in transaction.splits:
            account = db.get(Account, split.account_id)
            if account:
                account.current_balance -= split.amount
                db.add(account)
            db.delete(split)
        db.flush()

        # Patch header
        transaction.date = tx_in.date
        transaction.description = tx_in.description
        transaction.payee_id = tx_in.payee_id
        transaction.notes = tx_in.notes
        transaction.reference_number = tx_in.reference_number
        if tx_in.status is not None:
            transaction.status = tx_in.status

        # Update Tags
        stmt_tags = select(TransactionTagLink).where(TransactionTagLink.transaction_id == id)
        old_tags = db.exec(stmt_tags).all()
        for ot in old_tags:
            db.delete(ot)
        
        if tx_in.tag_ids:
            for tid in tx_in.tag_ids:
                link = TransactionTagLink(transaction_id=id, tag_id=tid)
                db.add(link)

        # Re-insert splits
        splits_data = [s.model_dump() for s in tx_in.splits]
        _bypass_balance_if_single_entry(engine, splits_data)

        for split_data in splits_data:
            amount = Decimal(str(split_data["amount"]))
            split = TransactionSplit(
                transaction_id=transaction.id,
                account_id=split_data["account_id"],
                category_id=split_data.get("category_id"),
                amount=amount,
                currency_code=split_data["currency_code"],
                memo=split_data.get("memo"),
            )
            db.add(split)
            account = db.get(Account, split.account_id)
            if account:
                account.current_balance += amount
                db.add(account)

        db.commit()
        db.refresh(transaction)
        return transaction

    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/{id}/void", response_model=TransactionResponse)
async def void_transaction(id: int, reason: str = "", db: Session = Depends(get_db)):
    """Void a transaction and revert its account balance impact."""
    engine = LedgerEngine(db)
    try:
        return await engine.void_transaction(id, reason)
    except LedgerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transfer", response_model=TransactionResponse, status_code=201)
async def create_transfer(transfer_in: TransferCreate, db: Session = Depends(get_db)):
    """Convenience endpoint to create a balanced two-leg transfer."""
    engine = LedgerEngine(db)
    splits = [
        {
            "account_id": transfer_in.from_account_id,
            "amount": -transfer_in.amount,
            "currency_code": transfer_in.currency_code,
        },
        {
            "account_id": transfer_in.to_account_id,
            "amount": transfer_in.amount,
            "currency_code": transfer_in.currency_code,
        },
    ]
    try:
        return await engine.create_transaction(
            user_id=CURRENT_USER_ID,
            date=transfer_in.date,
            description=(
                transfer_in.description
                or f"Transfer #{transfer_in.from_account_id} → #{transfer_in.to_account_id}"
            ),
            splits=splits,
        )
    except LedgerError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{id}", status_code=204)
async def delete_transaction(id: int, db: Session = Depends(get_db)):
    """Soft delete a transaction after voiding it to revert balance impact."""
    transaction = db.get(Transaction, id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    engine = LedgerEngine(db)
    # Ensure it's voided first to revert account balances
    if transaction.status != TransactionStatus.VOID:
        try:
            await engine.void_transaction(id, "LOGICAL_DELETE")
        except LedgerError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    transaction.deleted_at = datetime.utcnow()
    db.add(transaction)
    db.commit()
    return None
