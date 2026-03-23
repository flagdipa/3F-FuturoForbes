import os
import sys
from datetime import datetime
from decimal import Decimal
from sqlmodel import Session, create_engine, select, text, SQLModel
from dotenv import load_dotenv

# Path setup to import models correctly
sys.path.append(os.getcwd())

from backend.models.models_v2 import (
    User, Currency, Account, Category, Payee, 
    Transaction, TransactionSplit, TransactionStatus, AccountType
)

load_dotenv()

# Setup engines
SRC_URL = "mysql+pymysql://root:@localhost:3306/3f_db"
DEST_URL = os.getenv("DATABASE_URL", "sqlite:///3f_app.db")

src_engine = create_engine(SRC_URL)
dest_engine = create_engine(DEST_URL)

def migrate_v2():
    print("🚀 Iniciando migración masiva a V2 (Double-Entry)...")
    
    with Session(src_engine) as src, Session(dest_engine) as dest:
        # 0. Limpiar tablas destino (Eliminar datos de prueba)
        print("🧹 Limpiando tablas V2 actuales...")
        dest.execute(text("DELETE FROM transaction_splits"))
        dest.execute(text("DELETE FROM transaction_tag_link"))
        dest.execute(text("DELETE FROM transactions"))
        dest.execute(text("DELETE FROM payees"))
        dest.execute(text("DELETE FROM categories"))
        dest.execute(text("DELETE FROM accounts"))
        dest.execute(text("DELETE FROM users"))
        dest.execute(text("DELETE FROM currencies"))
        dest.commit()

        # 1. Usuarios
        print("👤 Migrando usuarios...")
        src_users = src.execute(text("SELECT * FROM usuarios")).all()
        user_map = {} # old_id -> new_id
        for u in src_users:
            new_u = User(
                email=u.email,
                hashed_password=u.password,
                full_name=f"{u.nombre or ''} {u.apellido or ''}".strip() or "Admin",
                is_active=True,
                is_admin=(u.rol_id == 1),
                theme_id=u.theme_preference or "3f-neon",
                language="es"
            )
            dest.add(new_u)
            dest.commit()
            dest.refresh(new_u)
            user_map[u.id_usuario] = new_u.id
        
        # Fallback if no users
        if not user_map:
            new_u = User(id=1, email="admin@3f.com", hashed_password="pbkdf2:sha256:...", full_name="Admin", is_admin=True)
            dest.add(new_u)
            dest.commit()
            user_map[1] = 1
        
        default_user_id = next(iter(user_map.values()))

        # 2. Divisas
        print("💱 Migrando divisas...")
        src_divs = src.execute(text("SELECT * FROM divisas")).all()
        for d in src_divs:
            new_d = Currency(
                code=d.codigo_iso,
                name=d.nombre_divisa,
                symbol=d.simbolo_prefijo or "$",
                decimal_places=d.decimal_places or 2,
                is_base=(d.codigo_iso == "ARS") # Assuming ARS is base
            )
            dest.add(new_d)
        dest.commit()

        # 3. Categorías
        print("📂 Migrando categorías...")
        src_cats = src.execute(text("SELECT * FROM categorias")).all()
        cat_map = {} # old_id -> new_id
        for c in src_cats:
            new_c = Category(
                user_id=default_user_id,
                name=c.nombre_categoria,
                type="EXPENSE", # Default, refined later if needed
                color=c.color,
                notes=c.notas
            )
            # Re-mapping hierarchy if exists
            dest.add(new_c)
            dest.commit()
            dest.refresh(new_c)
            cat_map[c.id_categoria] = new_c.id

        # 4. Beneficiarios
        print("🤝 Migrando beneficiarios...")
        src_payees = src.execute(text("SELECT * FROM beneficiarios")).all()
        payee_map = {} # old_id -> new_id
        for p in src_payees:
            new_p = Payee(
                user_id=default_user_id,
                name=p.nombre_beneficiario,
                default_category_id=cat_map.get(p.id_categoria),
                notes=p.notas,
                address=p.direccion,
                website=p.sitio_web
            )
            dest.add(new_p)
            dest.commit()
            dest.refresh(new_p)
            payee_map[p.id_beneficiario] = new_p.id

        # 5. Cuentas
        print("🏦 Migrando cuentas...")
        src_accs = src.execute(text("SELECT * FROM lista_cuentas")).all()
        acc_map = {} # old_id -> new_id
        for a in src_accs:
            # Map old divisas ID to code
            src_div = src.execute(text("SELECT codigo_iso FROM divisas WHERE id_divisa = :id"), {"id": a.id_divisa}).first()
            div_code = src_div[0] if src_div else "ARS"

            new_a = Account(
                user_id=default_user_id,
                name=a.nombre_cuenta,
                type=AccountType.ASSET if "Credit" not in a.tipo_cuenta else AccountType.LIABILITY,
                currency_code=div_code,
                account_number=a.numero_cuenta,
                initial_balance=Decimal(str(a.saldo_inicial)),
                current_balance=Decimal(str(a.saldo_inicial)), # Will be updated by transactions
                notes=a.notas,
                is_active=(a.estado == "Open")
            )
            dest.add(new_a)
            dest.commit()
            dest.refresh(new_a)
            acc_map[a.id_cuenta] = new_a.id

        # 6. Transacciones (The big conversion)
        print("💸 Convirtiendo y migrando transacciones...")
        src_txs = src.execute(text("SELECT * FROM libro_transacciones ORDER BY fecha_transaccion ASC")).all()
        
        count = 0
        for t in src_txs:
            # Convert string date to datetime
            try:
                dt = datetime.fromisoformat(t.fecha_transaccion) if t.fecha_transaccion else datetime.utcnow()
            except:
                dt = datetime.utcnow()

            # Create Header
            new_tx = Transaction(
                user_id=default_user_id,
                date=dt,
                description=t.notas or t.codigo_transaccion,
                payee_id=payee_map.get(t.id_beneficiario),
                status=TransactionStatus.RECONCILED, # Assuming history is reconciled
                reference_number=t.numero_transaccion,
                notes=t.notas
            )
            dest.add(new_tx)
            dest.commit()
            dest.refresh(new_tx)

            # Determine Amount Sign
            # Old system: Withdrawal/Expense = positive amount but logically subtracted? 
            # Actually most old 3F systems stored Withdrawal as positive amount and codigo_transaccion='Withdrawal'
            amount = Decimal(str(t.monto_transaccion))
            if t.codigo_transaccion in ['Withdrawal', 'Expense', 'Ajuste Negativo']:
                amount = -amount
            
            # Leg 1: Source Account
            new_acc_id = acc_map.get(t.id_cuenta)
            if new_acc_id:
                # Get currency from account
                acc_obj = dest.get(Account, new_acc_id)
                split1 = TransactionSplit(
                    transaction_id=new_tx.id,
                    account_id=new_acc_id,
                    category_id=cat_map.get(t.id_categoria),
                    amount=amount,
                    currency_code=acc_obj.currency_code if acc_obj else "ARS",
                    memo=t.notas
                )
                dest.add(split1)
                
                # Update Balance
                if acc_obj:
                    acc_obj.current_balance += amount
                    dest.add(acc_obj)

            # Leg 2: If it's a transfer
            if t.codigo_transaccion == 'Transfer' and t.id_cuenta_destino:
                new_dest_acc_id = acc_map.get(t.id_cuenta_destino)
                if new_dest_acc_id:
                    acc_dest_obj = dest.get(Account, new_dest_acc_id)
                    dest_amount = Decimal(str(t.monto_cuenta_destino or t.monto_transaccion))
                    split2 = TransactionSplit(
                        transaction_id=new_tx.id,
                        account_id=new_dest_acc_id,
                        amount=dest_amount,
                        currency_code=acc_dest_obj.currency_code if acc_dest_obj else "ARS",
                        memo=f"Transfer from {acc_obj.name if acc_obj else '?'}"
                    )
                    dest.add(split2)
                    if acc_dest_obj:
                        acc_dest_obj.current_balance += dest_amount
                        dest.add(acc_dest_obj)

            count += 1
            if count % 500 == 0:
                dest.commit()
                print(f"  - {count} transacciones procesadas...")
        
        dest.commit()
        print(f"✅ Migración V2 finalizada. Total: {count} transacciones migradas a la nueva estructura.")

if __name__ == "__main__":
    migrate_v2()
