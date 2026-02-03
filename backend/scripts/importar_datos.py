import subprocess
import os
import sys
import decimal
from datetime import datetime
from dotenv import load_dotenv

# Cargar variables de entorno desde el raíz
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")))

# Redirigir DB URL a localhost para ejecución desde el host Windows
db_url = os.getenv("DATABASE_URL")
if db_url and "@db:" in db_url:
    os.environ["DATABASE_URL"] = db_url.replace("@db:", "@localhost:")

# Añadir el path del backend para importar los modelos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlmodel import Session, select
from models.models import (
    Divisa, Categoria, Beneficiario, ListaCuentas, 
    LibroTransacciones, TransaccionDividida
)
from core.database import engine as pg_engine

def run_mysql_query(query):
    cmd = ["mysql", "-u", "root", "-pFer21gon", "-D", "futuroforbes_db", "-B", "-N", "-e", query]
    try:
        result = subprocess.run(cmd, capture_output=True, check=True)
        stdout_str = result.stdout.decode('utf-8', errors='ignore')
        lines = stdout_str.strip().split("\n")
        rows = []
        for line in lines:
            if not line or line.startswith("mysql:") or "Using a password" in line:
                continue
            rows.append(line.split("\t"))
        return rows
    except Exception as e:
        print(f"❌ Error MySQL: {e}")
        return []

def migrar_datos():
    print("🚀 Sincronizando datos desde futuroforbes_db...")
    
    with Session(pg_engine) as session:
        # 1. Divisas
        print("Sincronizando divisas...")
        for row in run_mysql_query("SELECT id_divisa, nombre_divisa, codigo_iso, simbolo_prefijo, tipo_divisa FROM divisas"):
            try:
                id_v = int(row[0])
                if not session.get(Divisa, id_v):
                    session.add(Divisa(id_divisa=id_v, nombre_divisa=row[1], codigo_iso=row[2], simbolo_prefijo=row[3] if row[3] != "NULL" else None, tipo_divisa=row[4]))
            except: continue
        session.commit()

        # 2. Categorías
        print("Sincronizando categorías...")
        cat_rows = run_mysql_query("SELECT id_categoria, nombre_categoria, activo, id_padre, color FROM categorias")
        for row in cat_rows:
            try:
                id_v = int(row[0])
                if not session.get(Categoria, id_v):
                    session.add(Categoria(id_categoria=id_v, nombre_categoria=row[1], activo=int(row[2]), id_padre=None, color=row[4] if row[4] != "NULL" else None))
            except: continue
        session.commit()
        
        # Actualizar jerarquía
        for row in cat_rows:
            try:
                id_v, id_p = int(row[0]), (int(row[3]) if row[3] != "NULL" else None)
                if id_p:
                    c = session.get(Categoria, id_v)
                    if c: c.id_padre = id_p
                    session.add(c)
            except: continue
        session.commit()

        # 3. Beneficiarios
        print("Sincronizando beneficiarios...")
        for row in run_mysql_query("SELECT id_beneficiario, nombre_beneficiario, id_categoria FROM beneficiarios"):
            try:
                id_v = int(row[0])
                if not session.get(Beneficiario, id_v):
                    session.add(Beneficiario(id_beneficiario=id_v, nombre_beneficiario=row[1], id_categoria=int(row[2]) if row[2] != "NULL" else None))
            except: continue
        session.commit()

        # 4. Cuentas
        print("Sincronizando cuentas...")
        for row in run_mysql_query("SELECT id_cuenta, nombre_cuenta, tipo_cuenta, id_divisa, saldo_inicial FROM lista_cuentas"):
            try:
                id_v = int(row[0])
                if not session.get(ListaCuentas, id_v):
                    session.add(ListaCuentas(id_cuenta=id_v, nombre_cuenta=row[1], tipo_cuenta=row[2], id_divisa=int(row[3]), saldo_inicial=decimal.Decimal(row[4])))
            except: continue
        session.commit()

        # 5. Transacciones (Batch 500)
        print("Sincronizando últimas 500 transacciones...")
        for row in run_mysql_query("SELECT id_transaccion, id_cuenta, id_beneficiario, codigo_transaccion, monto_transaccion, id_categoria, fecha_transaccion, es_dividida FROM libro_transacciones ORDER BY id_transaccion DESC LIMIT 500"):
            try:
                id_v = int(row[0])
                if not session.get(LibroTransacciones, id_v):
                    session.add(LibroTransacciones(
                        id_transaccion=id_v, id_cuenta=int(row[1]), id_beneficiario=int(row[2]),
                        codigo_transaccion=row[3], monto_transaccion=decimal.Decimal(row[4]),
                        id_categoria=int(row[5]) if row[5] != "NULL" else None,
                        fecha_transaccion=row[6], es_dividida=bool(int(row[7])) if (len(row)>7 and row[7] != "NULL") else False
                    ))
            except: continue
        session.commit()

    print("✅ Sincronización exitosa.")

if __name__ == "__main__":
    migrar_datos()
