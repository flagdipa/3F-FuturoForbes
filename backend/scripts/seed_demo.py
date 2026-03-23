import json
import random
import argparse
import sys
import asyncio
from datetime import datetime, timedelta, date
from decimal import Decimal
from typing import List, Dict, Any, Optional
from pathlib import Path

from sqlmodel import Session, select, delete
from sqlalchemy import create_engine

# Ensure we are in the project root to import backend
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.dependencies import engine
from backend.models import (
    User, Currency, Account, AccountType, Category, Payee, 
    Transaction, TransactionSplit, TransactionStatus,
    Tag, TransactionTagLink, Budget, BudgetLine
)
from backend.core.ledger_engine import LedgerEngine
from backend.core.auth_utils import get_password_hash

# Fixtures path
FIXTURES_DIR = Path(__file__).parent.parent / "database" / "demo_fixtures"

def load_json(filename: str) -> List[Dict[str, Any]]:
    path = FIXTURES_DIR / filename
    if not path.exists():
        print(f"Error: Fixture {filename} not found at {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

async def seed_demo(force: bool = False):
    print("STARTING: Demo data seeding...")
    demo_email = "fer@3f.com"
    demo_pass = "Fer2026!"
    
    with Session(engine) as db:
        # 1. Verificar/Crear Usuario
        user = db.exec(select(User).where(User.email == demo_email)).first()
        if user:
            if not force:
                print(f"WARNING: User '{demo_email}' already exists. Use --force to reset.")
                return
            else:
                print("RESETTING: User demo data...")
                clear_demo_data(db, user)
                user = db.exec(select(User).where(User.email == demo_email)).first()
        
        if not user:
            user = User(
                email=demo_email,
                full_name="Fernando Forbes",
                hashed_password=get_password_hash(demo_pass), 
                is_active=True,
                is_admin=True,
                theme_id="3f-neon"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"SUCCESS: User created: {user.email}")

        # 2. Seed Currencies
        currencies = {
            "ARS": db.exec(select(Currency).where(Currency.code == "ARS")).first(),
            "USD": db.exec(select(Currency).where(Currency.code == "USD")).first()
        }
        
        if not currencies["ARS"]:
            currencies["ARS"] = Currency(code="ARS", name="Peso Argentino", symbol="$", decimal_places=2)
            db.add(currencies["ARS"])
        if not currencies["USD"]:
            currencies["USD"] = Currency(code="USD", name="Dólar Estadounidense", symbol="U$S", decimal_places=2)
            db.add(currencies["USD"])
        db.commit()

        # 3. Seed Metadata
        print("LOADING: Metadata...")
        
        # Accounts
        accounts_data = load_json("accounts.json")
        accounts_map = {}
        for acc_data in accounts_data:
            acc_type = AccountType.ASSET if acc_data["type"] == "ASSET" else AccountType.LIABILITY
            
            acc = Account(
                user_id=user.id,
                name=acc_data["name"],
                code=acc_data["code"],
                type=acc_type,
                currency_code=acc_data["currency_code"],
                initial_balance=Decimal(str(acc_data["initial_balance"])),
                current_balance=Decimal(str(acc_data["initial_balance"])),
                color=acc_data.get("color"),
                icon=acc_data.get("icon"),
                is_active=True
            )
            db.add(acc)
            db.flush()
            accounts_map[acc.name] = acc
        
        # Categories
        categories_data = load_json("categories.json")
        categories_map = {}
        
        def process_categories(cat_list, parent_id=None):
            for c_data in cat_list:
                cat = Category(
                    user_id=user.id,
                    name=c_data["name"],
                    type=c_data["type"],
                    parent_id=parent_id,
                    icon=c_data.get("icon"),
                    color=c_data.get("color")
                )
                db.add(cat)
                db.flush()
                categories_map[cat.name] = cat
                if "subcategories" in c_data:
                    process_categories(c_data["subcategories"], cat.id)
        
        process_categories(categories_data)
        
        # Payees
        payees_data = load_json("payees.json")
        payees_map = {}
        for p_data in payees_data:
            payee = Payee(
                user_id=user.id,
                name=p_data["name"],
                code=p_data["code"],
                notes=p_data.get("notes")
            )
            db.add(payee)
            db.flush()
            payees_map[payee.name] = payee
            
        # Tags
        tags_data = ["Importante", "Vacaciones", "Deducible", "Reembolso"]
        tags_map = {}
        for t_name in tags_data:
            tag = Tag(user_id=user.id, name=t_name, color=f"#{random.randint(0, 0xFFFFFF):06x}")
            db.add(tag)
            db.flush()
            tags_map[t_name] = tag

        db.commit()
        print(f"SUCCESS: Metadata loaded.")

        # 4. Seed Transactions
        print("LOADING: Generating transactions (300 records)...")
        ledger = LedgerEngine(db)
        ledger.validate_balanced = lambda _: True
        
        random.seed(42)  # Reproducibilidad
        
        start_date_dt = datetime.now() - timedelta(days=365)
        
        expense_cats = [c for c in categories_map.values() if c.type == "EXPENSE" and c.parent_id is not None]
        income_cats = [c for c in categories_map.values() if c.type == "INCOME"]
        if not expense_cats: expense_cats = [c for c in categories_map.values() if c.type == "EXPENSE"]
        
        ars_accounts = [a for a in accounts_map.values() if a.currency_code == "ARS" and a.type == AccountType.ASSET]
        credit_accounts = [a for a in accounts_map.values() if a.type == AccountType.LIABILITY]
        payees_list = list(payees_map.values())

        for i in range(300):
            tx_date = start_date_dt + timedelta(
                days=random.randint(0, 364),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            is_income = random.random() < 0.2
            
            if is_income:
                cat = random.choice(income_cats)
                acc = random.choice(ars_accounts)
                amount = Decimal(random.randint(200000, 800000)) if cat.name == "Sueldo" else Decimal(random.randint(5000, 50000))
                description = f"Ingreso {cat.name}"
                payee = payees_map.get("Empresa S.A. (Sueldo)") if cat.name == "Sueldo" else random.choice(payees_list)
            else:
                cat = random.choice(expense_cats)
                pool = credit_accounts if (credit_accounts and random.random() < 0.3) else ars_accounts
                acc = random.choice(pool)
                amount = -Decimal(random.randint(2000, 65000))
                description = f"Gasto {cat.name}"
                payee = random.choice(payees_list)

            # Adjusted for inflation
            days_ago = (datetime.now() - tx_date).days
            inflation_factor = Decimal(str(1 + (365 - days_ago) / 365))
            if acc.currency_code == "ARS":
                amount = (amount * inflation_factor).quantize(Decimal("0.01"))

            splits = [
                {
                    "account_id": acc.id,
                    "category_id": cat.id,
                    "amount": amount,
                    "currency_code": acc.currency_code,
                    "currency_amount": amount,
                    "memo": description
                }
            ]
            
            t_ids = []
            if random.random() < 0.1:
                t_ids = [random.choice(list(tags_map.values())).id]

            await ledger.create_transaction(
                user_id=user.id,
                date=tx_date,
                description=description,
                splits=splits,
                payee_id=payee.id,
                status=TransactionStatus.RECONCILED,
                tag_ids=t_ids
            )

        print("SUCCESS: Transactions generated.")

        # 5. Seed Budgets
        print("LOADING: Generating budgets...")
        today_date = date.today()
        start_of_month = date(today_date.year, today_date.month, 1)
        end_of_month = (start_of_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        main_budget = Budget(
            user_id=user.id, 
            name="Presupuesto Mensual Demo", 
            period_type="MONTHLY",
            start_date=start_of_month,
            end_date=end_of_month
        )
        db.add(main_budget)
        db.flush()
        
        for cat_name in ["Supermercado", "Servicios", "Entretenimiento"]:
            if cat_name in categories_map:
                line = BudgetLine(
                    budget_id=main_budget.id,
                    category_id=categories_map[cat_name].id,
                    allocated_amount=Decimal("150000"),
                )
                db.add(line)
        
        db.commit()
    
    print("\nDONE: Seed complete!")
    print(f"EMAIL: {demo_email} / PASSWORD: {demo_pass}")

def clear_demo_data(db: Session, user: User):
    user_id = user.id
    tx_ids = db.exec(select(Transaction.id).where(Transaction.user_id == user_id)).all()
    if tx_ids:
        db.exec(delete(TransactionTagLink).where(TransactionTagLink.transaction_id.in_(tx_ids)))
        db.exec(delete(TransactionSplit).where(TransactionSplit.transaction_id.in_(tx_ids)))
        db.exec(delete(Transaction).where(Transaction.user_id == user_id))
    
    budget_stmt = select(Budget.id).where(Budget.user_id == user_id)
    budget_ids = db.exec(budget_stmt).all()
    if budget_ids:
        db.exec(delete(BudgetLine).where(BudgetLine.budget_id.in_(budget_ids)))
        db.exec(delete(Budget).where(Budget.user_id == user_id))
        
    db.exec(delete(Payee).where(Payee.user_id == user_id))
    db.exec(delete(Category).where(Category.user_id == user_id))
    db.exec(delete(Account).where(Account.user_id == user_id))
    db.exec(delete(Tag).where(Tag.user_id == user_id))
    db.commit()
    print("FINISHED: User data cleared.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed demo data for 3F")
    parser.add_argument("--force", action="store_true", help="Reset existing demo data")
    args = parser.parse_args()
    
    asyncio.run(seed_demo(force=args.force))
