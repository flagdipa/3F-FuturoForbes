import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.core.database import engine
from sqlmodel import Session, select
from backend.models import Account, Category, Payee, Tag, Transaction, TransactionSplit
from datetime import datetime, timedelta
from decimal import Decimal

def seed_db():
    with Session(engine) as session:
        # Check if already seeded to avoid duplicates
        existing_txs = session.exec(select(Transaction)).first()
        if existing_txs:
            print("Base de datos ya contiene transacciones, saltando seed.")
            return

        print("Inyectando datos de prueba...")
        user_id = 1 # Admin
        
        # 1. Accounts
        acc_cash = Account(user_id=user_id, name="Billetera Efectivo", type="ASSET", currency_code="USD", current_balance=150)
        acc_bank = Account(user_id=user_id, name="Banco Galicia", type="ASSET", currency_code="USD", current_balance=2500)
        acc_cc = Account(user_id=user_id, name="Tarjeta Master", type="LIABILITY", currency_code="USD", current_balance=-400)
        session.add(acc_cash)
        session.add(acc_bank)
        session.add(acc_cc)
        
        # 2. Categories
        cat_salary = Category(user_id=user_id, name="Salarios", type="INCOME", color="#2ecc71")
        cat_food = Category(user_id=user_id, name="Supermercado", type="EXPENSE", color="#e74c3c")
        cat_leisure = Category(user_id=user_id, name="Ocio", type="EXPENSE", color="#9b59b6")
        session.add(cat_salary)
        session.add(cat_food)
        session.add(cat_leisure)
        
        # 3. Beneficiarios (Payees)
        p_work = Payee(user_id=user_id, name="Empresa de Software S.A.")
        p_super = Payee(user_id=user_id, name="Walmart")
        p_cinema = Payee(user_id=user_id, name="Cines Hoyts")
        session.add(p_work)
        session.add(p_super)
        session.add(p_cinema)
        
        # 4. Tags
        t_urgent = Tag(user_id=user_id, name="Urgente", color="#ff0000")
        t_fun = Tag(user_id=user_id, name="Diversión", color="#00ff00")
        session.add(t_urgent)
        session.add(t_fun)
        
        session.commit()
        
        # Refetch to get IDs mapping
        acc_cash_id = acc_cash.id
        acc_bank_id = acc_bank.id
        acc_cc_id = acc_cc.id
        cat_salary_id = cat_salary.id
        cat_food_id = cat_food.id
        cat_leisure_id = cat_leisure.id
        p_work_id = p_work.id
        p_super_id = p_super.id
        
        # 5. Transactions
        now = datetime.utcnow()
        
        # Income Transaction (Salary deposited to Bank)
        tx1 = Transaction(user_id=user_id, date=now - timedelta(days=5), description="Sueldo Quincena", payee_id=p_work_id, status="RECONCILED")
        session.add(tx1)
        session.commit()
        s1 = TransactionSplit(transaction_id=tx1.id, account_id=acc_bank_id, category_id=cat_salary_id, amount=Decimal("2000.00"), currency_code="USD")
        session.add(s1)
        
        # Expense Transaction (Supermarket paid with Cash)
        tx2 = Transaction(user_id=user_id, date=now - timedelta(days=2), description="Compra de víveres mensuales", payee_id=p_super_id, status="PENDING")
        session.add(tx2)
        session.commit()
        s2 = TransactionSplit(transaction_id=tx2.id, account_id=acc_cash_id, category_id=cat_food_id, amount=Decimal("-150.00"), currency_code="USD")
        session.add(s2)
        
        # Expense Transaction (Leisure paid with CC)
        tx3 = Transaction(user_id=user_id, date=now - timedelta(days=1), description="Entradas Cine", payee_id=p_cinema.id, status="PENDING")
        session.add(tx3)
        session.commit()
        s3 = TransactionSplit(transaction_id=tx3.id, account_id=acc_cc_id, category_id=cat_leisure_id, amount=Decimal("-25.50"), currency_code="USD")
        session.add(s3)
        
        session.commit()
        print("Migración y carga de datos de prueba exitosa.")

if __name__ == '__main__':
    seed_db()
