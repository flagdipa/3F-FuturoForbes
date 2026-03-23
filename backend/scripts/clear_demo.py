import argparse
import sys
from pathlib import Path
from sqlmodel import Session, select, delete

# Ensure we are in the project root to import backend
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.dependencies import engine
from backend.models import (
    User, Account, Category, Payee, 
    Transaction, TransactionSplit, TransactionTagLink,
    Budget, BudgetLine, Tag
)

def clear_demo_by_email(db, email):
    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        return False
        
    user_id = user.id
    print(f"🧹 Limpiando usuario: {email} (ID={user_id})")
    
    # Transactions and its links
    tx_ids = db.exec(select(Transaction.id).where(Transaction.user_id == user_id)).all()
    if tx_ids:
        db.exec(delete(TransactionTagLink).where(TransactionTagLink.transaction_id.in_(tx_ids)))
        db.exec(delete(TransactionSplit).where(TransactionSplit.transaction_id.in_(tx_ids)))
        db.exec(delete(Transaction).where(Transaction.user_id == user_id))

    # Budgets
    budget_ids = db.exec(select(Budget.id).where(Budget.user_id == user_id)).all()
    if budget_ids:
        db.exec(delete(BudgetLine).where(BudgetLine.budget_id.in_(budget_ids)))
        db.exec(delete(Budget).where(Budget.user_id == user_id))

    # Metadata
    db.exec(delete(Payee).where(Payee.user_id == user_id))
    db.exec(delete(Category).where(Category.user_id == user_id))
    db.exec(delete(Account).where(Account.user_id == user_id))
    db.exec(delete(Tag).where(Tag.user_id == user_id))
    
    db.exec(delete(User).where(User.id == user_id))
    db.commit()
    return True

def clear_all_demos():
    emails = ["demo@3f.local", "demo@example.com", "fer@3f.com"]
    with Session(engine) as db:
        for email in emails:
            if clear_demo_by_email(db, email):
                print(f"✅ Usuario {email} eliminado.")
    print("\n✨ Limpieza total finalizada.")

if __name__ == "__main__":
    clear_all_demos()
