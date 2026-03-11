from decimal import Decimal
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlmodel import select, func
from ..models import Transaction, TransactionSplit, TransactionStatus, Account

class LedgerError(Exception):
    pass

class LedgerEngine:
    """
    Core accounting engine for 3F.
    Enforces double-entry rules and manages balances.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def validate_balanced(self, splits: List[Dict[str, Any]]) -> bool:
        """Enforce that debits and credits sum up to zero."""
        total = sum(Decimal(str(s.get('amount', 0))) for s in splits)
        return total == Decimal('0')

    async def create_transaction(
        self, 
        user_id: int,
        date: datetime,
        description: str,
        splits: List[Dict[str, Any]],
        payee_id: Optional[int] = None,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None,
        status: Optional[TransactionStatus] = None,
        tag_ids: Optional[List[int]] = None
    ) -> Transaction:
        """
        Creates a new transaction with its associated splits and tags.
        Atomically updates account balances.
        """
        if not self.validate_balanced(splits):
            raise LedgerError("Transaction is not balanced. The sum of splits must be zero.")

        # Create Transaction Header
        transaction = Transaction(
            user_id=user_id,
            date=date,
            description=description,
            payee_id=payee_id,
            reference_number=reference_number,
            notes=notes,
            status=status or TransactionStatus.PENDING
        )
        self.db.add(transaction)
        self.db.flush() # Get transaction ID

        # Link Tags
        if tag_ids:
            from ..models import TransactionTagLink
            for tid in tag_ids:
                link = TransactionTagLink(transaction_id=transaction.id, tag_id=tid)
                self.db.add(link)

        # Process Splits and update balances
        for split_data in splits:
            split = TransactionSplit(
                transaction_id=transaction.id,
                account_id=split_data['account_id'],
                category_id=split_data.get('category_id'),
                amount=Decimal(str(split_data['amount'])),
                currency_code=split_data['currency_code'],
                currency_amount=Decimal(str(split_data['currency_amount'] if split_data.get('currency_amount') is not None else split_data['amount'])),
                memo=split_data.get('memo')
            )
            self.db.add(split)
            
            # Update Account Balance
            account = self.db.get(Account, split.account_id)
            if account:
                account.current_balance += split.amount
                self.db.add(account)

        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    async def void_transaction(self, transaction_id: int, reason: str = "") -> Transaction:
        """
        Anulates a transaction by creating a reversal or simplemente marking as VOID 
        and reverting balances. For full double-entry audit, a reversal transaction is better,
        but simple voiding is supported here for UX.
        """
        transaction = self.db.get(Transaction, transaction_id)
        if not transaction:
            raise LedgerError("Transaction not found")
        
        if transaction.status == TransactionStatus.VOID:
            return transaction

        # Revert Account Balances
        statement = select(TransactionSplit).where(TransactionSplit.transaction_id == transaction_id)
        splits = self.db.exec(statement).all()
        
        for split in splits:
            account = self.db.get(Account, split.account_id)
            if account:
                account.current_balance -= split.amount
                self.db.add(account)

        transaction.status = TransactionStatus.VOID
        transaction.notes = f"{transaction.notes or ''}\nVOID REASON: {reason}".strip()
        self.db.add(transaction)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def get_account_balance(self, account_id: int, date_at: Optional[datetime] = None) -> Decimal:
        """Calculates balance as sum of all splits until a certain date."""
        query = select(func.sum(TransactionSplit.amount)).where(TransactionSplit.account_id == account_id)
        
        if date_at:
            query = query.join(Transaction).where(Transaction.date <= date_at)
            
        result = self.db.exec(query).first()
        return Decimal(str(result or 0))

    def get_account_register(self, account_id: int, limit: int = 50, offset: int = 0) -> List[Any]:
        """Returns the ledger entries for a specific account."""
        statement = (
            select(Transaction, TransactionSplit)
            .join(TransactionSplit)
            .where(TransactionSplit.account_id == account_id)
            .order_by(Transaction.date.desc())
            .offset(offset).limit(limit)
        )
        return self.db.exec(statement).all()

    async def reconcile_account(self, account_id: int, statement_balance: Decimal, statement_date: datetime):
        """
        Marks all pending splits until statement_date as reconciled if they match logic.
        This is a simplified version.
        """
        # 1. Get current calculated balance until statement_date
        current_calc = self.get_account_balance(account_id, statement_date)
        
        if current_calc != statement_balance:
            raise LedgerError(f"Reconciliation failed. Calculated: {current_calc}, Statement: {statement_balance}")

        # 2. Mark all splits as reconciled
        statement = (
            select(TransactionSplit)
            .join(Transaction)
            .where(TransactionSplit.account_id == account_id)
            .where(Transaction.date <= statement_date)
            .where(TransactionSplit.reconciled == False)
        )
        splits = self.db.exec(statement).all()
        for split in splits:
            split.reconciled = True
            self.db.add(split)
        
        self.db.commit()
