#!/usr/bin/env python3
"""
Script para poblar la base de datos con datos de prueba realistas
Uso: python scripts/seed_demo_data.py
"""
import sys
from pathlib import Path

# Agregar el directorio raiz al path
root_path = Path(__file__).parent.parent
sys.path.insert(0, str(root_path))

from sqlmodel import Session, select
from datetime import datetime, timedelta
from decimal import Decimal
import random

from backend.core.database import engine
from backend.models.models_v2 import (
    User, Currency, Account, AccountType, Category, Payee,
    Transaction, TransactionSplit, TransactionStatus
)

def seed_demo_data():
    """Crea datos de prueba realistas en la base de datos"""
    
    with Session(engine) as session:
        # 1. Crear usuario demo
        user = session.exec(select(User).where(User.email == "demo@3f.com")).first()
        if not user:
            user = User(
                email="demo@3f.com",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYMyzJ.IwG",
                full_name="Usuario Demo",
                is_active=True,
                is_admin=False
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print("[OK] Usuario creado: {}".format(user.email))
        else:
            print("[OK] Usuario ya existe: {}".format(user.email))
        
        # 2. Crear monedas
        currencies_data = [
            {"code": "ARS", "name": "Peso Argentino", "symbol": "$", "is_base": True},
            {"code": "USD", "name": "Dolar Estadounidense", "symbol": "US$", "is_base": False},
            {"code": "USDT", "name": "Dolar Crypto", "symbol": "USDT", "is_base": False},
        ]
        
        for curr_data in currencies_data:
            existing = session.exec(select(Currency).where(Currency.code == curr_data["code"])).first()
            if not existing:
                currency = Currency(**curr_data)
                session.add(currency)
                print("[OK] Moneda creada: {}".format(curr_data["code"]))
            else:
                print("[OK] Moneda ya existe: {}".format(curr_data["code"]))
        
        session.commit()
        
        # 3. Crear cuentas
        accounts_data = [
            {"name": "Efectivo", "type": AccountType.ASSET, "currency_code": "ARS", "initial_balance": Decimal("15000.00")},
            {"name": "Banco Galicia", "type": AccountType.ASSET, "currency_code": "ARS", "initial_balance": Decimal("125000.00")},
            {"name": "Mercado Pago", "type": AccountType.ASSET, "currency_code": "ARS", "initial_balance": Decimal("45000.00")},
            {"name": "Cuenta Dolares", "type": AccountType.ASSET, "currency_code": "USD", "initial_balance": Decimal("500.00")},
            {"name": "Billetera Crypto", "type": AccountType.ASSET, "currency_code": "USDT", "initial_balance": Decimal("300.00")},
            {"name": "Tarjeta Credito Visa", "type": AccountType.LIABILITY, "currency_code": "ARS", "initial_balance": Decimal("-25000.00")},
        ]
        
        accounts = []
        for acc_data in accounts_data:
            existing = session.exec(
                select(Account).where(
                    Account.name == acc_data["name"],
                    Account.user_id == user.id
                )
            ).first()
            
            if not existing:
                account = Account(
                    user_id=user.id,
                    current_balance=acc_data["initial_balance"],
                    **{k: v for k, v in acc_data.items() if k != "initial_balance"}
                )
                session.add(account)
                session.commit()
                session.refresh(account)
                accounts.append(account)
                print("[OK] Cuenta creada: {} - ${}".format(account.name, account.current_balance))
            else:
                accounts.append(existing)
                print("[OK] Cuenta ya existe: {}".format(existing.name))
        
        # 4. Crear categorias
        categories_data = [
            {"name": "Sueldo", "type": "INCOME", "color": "#00ff88"},
            {"name": "Freelance", "type": "INCOME", "color": "#00ff88"},
            {"name": "Inversiones", "type": "INCOME", "color": "#00ff88"},
            {"name": "Regalos", "type": "INCOME", "color": "#00ff88"},
            {"name": "Alquiler", "type": "EXPENSE", "color": "#ff4444"},
            {"name": "Servicios", "type": "EXPENSE", "color": "#ff6666"},
            {"name": "Comida", "type": "EXPENSE", "color": "#ff8888"},
            {"name": "Transporte", "type": "EXPENSE", "color": "#ffaa88"},
            {"name": "Entretenimiento", "type": "EXPENSE", "color": "#ff88aa"},
            {"name": "Salud", "type": "EXPENSE", "color": "#ff4488"},
            {"name": "Educacion", "type": "EXPENSE", "color": "#ff66aa"},
            {"name": "Compras", "type": "EXPENSE", "color": "#ff99aa"},
            {"name": "Otros", "type": "EXPENSE", "color": "#ffaaaa"},
        ]
        
        categories = []
        for cat_data in categories_data:
            existing = session.exec(
                select(Category).where(
                    Category.name == cat_data["name"],
                    Category.user_id == user.id
                )
            ).first()
            
            if not existing:
                category = Category(user_id=user.id, **cat_data)
                session.add(category)
                session.commit()
                session.refresh(category)
                categories.append(category)
                print("[OK] Categoria creada: {}".format(category.name))
            else:
                categories.append(existing)
                print("[OK] Categoria ya existe: {}".format(existing.name))
        
        # 5. Crear beneficiarios
        payees_data = [
            {"name": "Supermercado Carrefour", "website": "carrefour.com.ar"},
            {"name": "YPF", "website": "ypf.com"},
            {"name": "Uber", "website": "uber.com"},
            {"name": "Netflix", "website": "netflix.com"},
            {"name": "Spotify", "website": "spotify.com"},
            {"name": "Farmacia", "website": ""},
            {"name": "Restaurante", "website": ""},
            {"name": "Gas", "website": ""},
            {"name": "Electricidad", "website": ""},
            {"name": "Internet", "website": ""},
            {"name": "Celular", "website": ""},
            {"name": "Gimnasio", "website": ""},
        ]
        
        payees = []
        for payee_data in payees_data:
            existing = session.exec(
                select(Payee).where(
                    Payee.name == payee_data["name"],
                    Payee.user_id == user.id
                )
            ).first()
            
            if not existing:
                payee = Payee(user_id=user.id, **payee_data)
                session.add(payee)
                session.commit()
                session.refresh(payee)
                payees.append(payee)
                print("[OK] Beneficiario creado: {}".format(payee.name))
            else:
                payees.append(existing)
                print("[OK] Beneficiario ya existe: {}".format(existing.name))
        
        # 6. Crear transacciones de prueba (ultimos 3 meses)
        income_categories = [c for c in categories if c.type == "INCOME"]
        expense_categories = [c for c in categories if c.type == "EXPENSE"]
        
        transactions_created = 0
        
        # Crear transacciones aleatorias para los ultimos 90 dias
        for day in range(90):
            current_date = datetime.now() - timedelta(days=day)
            
            # 30% de probabilidad de transaccion por dia
            if random.random() < 0.3:
                # Decidir si es ingreso o gasto
                is_income = random.random() < 0.2  # 20% ingresos, 80% gastos
                
                if is_income and income_categories:
                    category = random.choice(income_categories)
                    amount = Decimal(str(random.uniform(5000, 50000)))
                    account = random.choice([a for a in accounts if a.type == AccountType.ASSET])
                    description = "Ingreso - {}".format(category.name)
                    payee = None
                elif expense_categories:
                    category = random.choice(expense_categories)
                    amount = Decimal(str(random.uniform(50, 5000)))
                    account = random.choice(accounts)
                    payee = random.choice(payees) if payees else None
                    description = "Gasto - {}".format(category.name)
                else:
                    continue
                
                # Crear transaccion
                transaction = Transaction(
                    user_id=user.id,
                    transaction_date=current_date.date(),
                    description=description,
                    status=TransactionStatus.CLEARED,
                    created_at=current_date,
                    updated_at=current_date
                )
                session.add(transaction)
                session.commit()
                session.refresh(transaction)
                
                # Crear split
                split = TransactionSplit(
                    transaction_id=transaction.id,
                    account_id=account.id,
                    category_id=category.id,
                    payee_id=payee.id if payee else None,
                    amount=amount,
                    currency_code=account.currency_code
                )
                session.add(split)
                
                # Actualizar saldo de cuenta
                if category.type == "INCOME":
                    account.current_balance += amount
                else:
                    account.current_balance -= amount
                
                transactions_created += 1
                
                if transactions_created % 10 == 0:
                    session.commit()
                    print("[PROGRESS] {} transacciones creadas...".format(transactions_created))
        
        session.commit()
        print("\n[OK] Se crearon {} transacciones de prueba".format(transactions_created))
        
        # Resumen final
        print("\n" + "="*60)
        print("RESUMEN DE DATOS CREADOS")
        print("="*60)
        print("Usuario: {} ({})".format(user.full_name, user.email))
        print("Password: demo123")
        print("")
        print("Cuentas: {}".format(len(accounts)))
        print("Categorias: {}".format(len(categories)))
        print("Beneficiarios: {}".format(len(payees)))
        print("Transacciones: {}".format(transactions_created))
        print("="*60)

if __name__ == "__main__":
    try:
        seed_demo_data()
        print("\n[OK] Base de datos poblada exitosamente!")
    except Exception as e:
        print("\n[ERROR] {}".format(e))
        import traceback
        traceback.print_exc()
