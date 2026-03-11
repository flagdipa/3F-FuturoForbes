import sqlite3
import os
import sys

from backend.core.database import engine
from sqlmodel import Session
from backend.models import User, Account, Category, Transaction, TransactionSplit, Currency
from datetime import datetime

def migrate():
    # SQLite connection to OLD db
    conn = sqlite3.connect('C:/xampp/htdocs/3F/legacy.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    with Session(engine) as session:
        print("Migrating Usuarios -> Users")
        c.execute("SELECT * FROM usuarios")
        users = c.fetchall()
        for u in users:
            try:
                user_exists = session.get(User, u['id_usuario'])
                if not user_exists:
                    nombre = u['nombre'] if u['nombre'] else ''
                    apellido = u['apellido'] if 'apellido' in u.keys() and u['apellido'] else ''
                    full_name = (nombre + ' ' + apellido).strip()
                    
                    new_user = User(
                        id=u['id_usuario'],
                        email=u['email'],
                        hashed_password=u['password'] if 'password' in u.keys() else 'none',
                        full_name=full_name if full_name else 'Usuario Sin Nombre',
                        is_active=True, # Assuming true
                        theme_id='dark_neon'
                    )
                    session.add(new_user)
            except Exception as e: print("SKIP USER", u['id_usuario'], e)
        session.commit()

        print("Migrating Categorias -> Categories")
        c.execute("SELECT * FROM categorias")
        cats = c.fetchall()
        for c_row in cats:
            cat_exists = session.get(Category, c_row['id_categoria'])
            if not cat_exists:
                ctype = "EXPENSE"
                name_str = c_row['nombre_categoria'].lower()
                if 'ingreso' in name_str or 'sueldo' in name_str or 'venta' in name_str or 'salario' in name_str:
                    ctype = "INCOME"
                
                new_cat = Category(
                    id=c_row['id_categoria'],
                    user_id=1,
                    name=c_row['nombre_categoria'],
                    type=ctype,
                    color=c_row['color'] if 'color' in c_row.keys() and c_row['color'] else '#FFFFFF'
                )
                session.add(new_cat)
        session.commit()
        
        print("Migrating Divisas -> Currencies")
        try:
            c.execute("SELECT * FROM divisas")
            divs = c.fetchall()
            id_to_code = {}
            for d in divs:
                if 'codigo' in d.keys(): code = d['codigo']
                else: code = str(d['id_divisa'])
                
                id_to_code[d['id_divisa']] = code
                
                curr_exists = session.get(Currency, code)
                if not curr_exists:
                    new_curr = Currency(
                        code=code,
                        name=d['nombre'] if 'nombre' in d.keys() else code,
                        symbol=d['simbolo'] if 'simbolo' in d.keys() else code
                    )
                    session.add(new_curr)
            session.commit()
        except sqlite3.OperationalError:
            print("Tabla divisas no encontrada, usando defautls.")
            id_to_code = {}
            
        print("Migrating ListaCuentas -> Accounts")
        c.execute("SELECT * FROM lista_cuentas")
        accounts = c.fetchall()
        for a in accounts:
            acc_exists = session.get(Account, a['id_cuenta'])
            if not acc_exists:
                currency_code = id_to_code.get(a['id_divisa'], 'USD') if 'id_divisa' in a.keys() else 'USD'
                
                # Use ASSET by default to avoid enum validation issues during migration
                new_acc = Account(
                    id=a['id_cuenta'],
                    user_id=a['id_usuario'],
                    name=a['nombre_cuenta'],
                    type='ASSET',
                    currency_code=currency_code, 
                    current_balance=a['saldo_actual'] if 'saldo_actual' in a.keys() else 0
                )
                session.add(new_acc)
        session.commit()

        print("Migrating LibroTransacciones -> Transactions/Splits")
        c.execute("SELECT * FROM libro_transacciones")
        txs = c.fetchall()
        for tx in txs:
            try:
                tx_exists = session.get(Transaction, tx['id_transaccion'])
                if not tx_exists:
                    fecha_str = tx['fecha_transaccion']
                    try:
                        fecha = datetime.fromisoformat(fecha_str.replace("Z", "+00:00"))
                    except:
                        try:
                            fecha = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
                        except:
                            fecha = datetime.utcnow()
                            
                    new_tx = Transaction(
                        id=tx['id_transaccion'],
                        user_id=tx['id_usuario'],
                        date=fecha,
                        status="RECONCILED",
                        description=tx['descripcion'] if 'descripcion' in tx.keys() else ''
                    )
                    session.add(new_tx)
                    session.flush() # flush to get id bound, though we enforce id anyway

                    monto = tx['monto_transaccion']
                    code_tx = tx['codigo_transaccion'] if 'codigo_transaccion' in tx.keys() else ''
                    is_deposit = (code_tx.lower() == 'deposit' or code_tx.lower() == 'ingreso')
                    
                    s1 = TransactionSplit(
                        transaction_id=tx['id_transaccion'],
                        account_id=tx['id_cuenta'],
                        amount=monto if is_deposit else -monto,
                        category_id=tx['id_categoria'] if 'id_categoria' in tx.keys() else None
                    )
                    session.add(s1)
            except Exception as e: print("SKIP TX", tx['id_transaccion'], e)
        session.commit()

    print("Migración completada.")

if __name__ == "__main__":
    migrate()
