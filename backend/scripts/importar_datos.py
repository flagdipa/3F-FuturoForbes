
import os
import sys
import decimal
import pymysql
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el raíz
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")))

# Añadir el path del backend para importar los modelos
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from sqlmodel import Session, select
from models.models import (
    Divisa, Categoria, Beneficiario, ListaCuentas, 
    LibroTransacciones, TransaccionDividida, Usuario
)
from core.database import engine as sqlite_engine

def get_mysql_data(query):
    # Intentamos conectar con root y sin password
    try:
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='3f_db',
            cursorclass=pymysql.cursors.DictCursor
        )
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        # Si falla, probamos con el password Fer21gon
        try:
            conn = pymysql.connect(
                host='localhost',
                user='root',
                password='Fer21gon',
                database='3f_db',
                cursorclass=pymysql.cursors.DictCursor
            )
            with conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e2:
            print(f"❌ Error MySQL (PyMySQL): {e2}")
            return []

def migrar_datos():
    print("🚀 Sincronizando datos desde 3f_db (MySQL) a 3f_app.db (SQLite) usando PyMySQL...")
    
    with Session(sqlite_engine) as session:
        # 0. Usuarios
        print("Sincronizando usuarios...")
        rows = get_mysql_data("SELECT id_usuario, email, password, rol_id FROM usuarios")
        for row in rows:
            try:
                id_v = row['id_usuario']
                if not session.get(Usuario, id_v):
                    session.add(Usuario(id_usuario=id_v, email=row['email'], password=row['password'], rol_id=row['rol_id']))
            except: continue
        session.commit()

        # 1. Divisas
        print("Sincronizando divisas...")
        rows = get_mysql_data("SELECT id_divisa, nombre_divisa, codigo_iso, simbolo_prefijo, tipo_divisa FROM divisas")
        for row in rows:
            try:
                id_v = row['id_divisa']
                if not session.get(Divisa, id_v):
                    session.add(Divisa(id_divisa=id_v, nombre_divisa=row['nombre_divisa'], codigo_iso=row['codigo_iso'], simbolo_prefijo=row['simbolo_prefijo'], tipo_divisa=row['tipo_divisa']))
            except: continue
        session.commit()

        # 2. Categorías
        print("Sincronizando categorías...")
        cat_rows = get_mysql_data("SELECT id_categoria, nombre_categoria, is_active, id_padre, color FROM categorias")
        for row in cat_rows:
            try:
                id_v = row['id_categoria']
                if not session.get(Categoria, id_v):
                    session.add(Categoria(id_categoria=id_v, nombre_categoria=row['nombre_categoria'], is_active=row['is_active'], id_padre=None, color=row['color']))
            except: continue
        session.commit()
        
        # Actualizar jerarquía
        for row in cat_rows:
            try:
                id_v, id_p = row['id_categoria'], row['id_padre']
                if id_p:
                    c = session.get(Categoria, id_v)
                    if c: c.id_padre = id_p
                    session.add(c)
            except: continue
        session.commit()

        # 3. Beneficiarios
        print("Sincronizando beneficiarios...")
        rows = get_mysql_data("SELECT id_beneficiario, nombre_beneficiario, id_categoria FROM beneficiarios")
        for row in rows:
            try:
                id_v = row['id_beneficiario']
                if not session.get(Beneficiario, id_v):
                    session.add(Beneficiario(id_beneficiario=id_v, nombre_beneficiario=row['nombre_beneficiario'], id_categoria=row['id_categoria']))
            except: continue
        session.commit()

        # 4. Cuentas
        print("Sincronizando cuentas...")
        rows = get_mysql_data("SELECT id_cuenta, nombre_cuenta, tipo_cuenta, id_divisa, saldo_inicial FROM lista_cuentas")
        for row in rows:
            try:
                id_v = row['id_cuenta']
                if not session.get(ListaCuentas, id_v):
                    session.add(ListaCuentas(id_cuenta=id_v, nombre_cuenta=row['nombre_cuenta'], tipo_cuenta=row['tipo_cuenta'], id_divisa=row['id_divisa'], saldo_inicial=decimal.Decimal(row['saldo_inicial'])))
            except: continue
        session.commit()

        # 5. Transacciones
        print("Sincronizando transacciones...")
        rows = get_mysql_data("SELECT id_transaccion, id_cuenta, id_beneficiario, codigo_transaccion, monto_transaccion, id_categoria, fecha_transaccion, es_dividida FROM libro_transacciones")
        for row in rows:
            try:
                id_v = row['id_transaccion']
                if not session.get(LibroTransacciones, id_v):
                    session.add(LibroTransacciones(
                        id_transaccion=id_v, id_cuenta=row['id_cuenta'], id_beneficiario=row['id_beneficiario'],
                        codigo_transaccion=row['codigo_transaccion'], monto_transaccion=decimal.Decimal(row['monto_transaccion']),
                        id_categoria=row['id_categoria'],
                        fecha_transaccion=str(row['fecha_transaccion']) if row['fecha_transaccion'] else None,
                        es_dividida=bool(row['es_dividida'])
                    ))
            except: continue
        session.commit()

        # 8. Transacciones Divididas (Splits)
        print("Sincronizando transacciones divididas...")
        rows = get_mysql_data("SELECT id_division, id_transaccion, id_categoria, monto_division, notas FROM transacciones_divididas")
        for row in rows:
            try:
                id_v = row['id_division']
                if not session.get(TransaccionDividida, id_v):
                    if session.get(LibroTransacciones, row['id_transaccion']):
                        session.add(TransaccionDividida(
                            id_division=id_v,
                            id_transaccion=row['id_transaccion'],
                            id_categoria=row['id_categoria'],
                            monto_division=decimal.Decimal(row['monto_division']),
                            notas=row['notas']
                        ))
            except Exception:
                continue
        session.commit()

    print("✅ Sincronización finalizada con éxito.")

if __name__ == "__main__":
    migrar_datos()
