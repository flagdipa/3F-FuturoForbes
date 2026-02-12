from sqlmodel import Session, create_engine, select, text
from backend.models.models import Beneficiario, LibroTransacciones, ListaCuentas
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup engine
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://root:@localhost:3306/3f_db?charset=utf8mb4"

engine = create_engine(DATABASE_URL)

def fix_encoding():
    print("🚀 Iniciando reparación de codificación UTF-8 (Intento 2)...")
    
    with Session(engine) as session:
        # 1. Fix Beneficiarios using SQL for precision
        print("🔧 Limpiando Beneficiarios...")
        # Direct verification of what we are about to change
        bens_to_fix = session.exec(text("SELECT id_beneficiario, nombre_beneficiario FROM beneficiarios WHERE nombre_beneficiario LIKE '%Naci-|-n%'")).all()
        print(f"   -> Encontrados {len(bens_to_fix)} beneficiarios corruptos.")
        
        # Execute direct update
        if bens_to_fix:
            session.exec(text("UPDATE beneficiarios SET nombre_beneficiario = REPLACE(nombre_beneficiario, 'Naci-|-n', 'Nación') WHERE nombre_beneficiario LIKE '%Naci-|-n%'"))
            session.commit()
            print("   ✅ Beneficiarios corregidos.")

        # 2. Fix Cuentas
        print("🔧 Limpiando Cuentas...")
        accs_to_fix = session.exec(text("SELECT id_cuenta, nombre_cuenta FROM lista_cuentas WHERE nombre_cuenta LIKE '%Naci-|-n%'")).all()
        print(f"   -> Encontradas {len(accs_to_fix)} cuentas corruptas.")
        
        if accs_to_fix:
            session.exec(text("UPDATE lista_cuentas SET nombre_cuenta = REPLACE(nombre_cuenta, 'Naci-|-n', 'Nación') WHERE nombre_cuenta LIKE '%Naci-|-n%'"))
            session.commit()
            print("   ✅ Cuentas corregidas.")

        # 3. Generic Fixes (Mojibake)
        print("🔧 Aplicando correcciones genéricas...")
        generic_fixes = [
            ("Ã³", "ó"), ("Ã¡", "á"), ("Ã©", "é"), ("Ã±", "ñ"), ("Ãº", "ú"), ("â€“", "-")
        ]
        
        tables = ["beneficiarios", "lista_cuentas", "categorias"]
        columns = {"beneficiarios": "nombre_beneficiario", "lista_cuentas": "nombre_cuenta", "categorias": "nombre_categoria"}
        
        for table in tables:
            col = columns[table]
            for bad, good in generic_fixes:
                sql = f"UPDATE {table} SET {col} = REPLACE({col}, '{bad}', '{good}') WHERE {col} LIKE '%{bad}%'"
                session.exec(text(sql))
            session.commit()
            print(f"   ✅ Tabla {table} procesada.")

    print("🏁 Proceso finalizado.")

if __name__ == "__main__":
    fix_encoding()
