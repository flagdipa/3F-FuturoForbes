from sqlmodel import Session, create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://root:@localhost:3306/3f_db?charset=utf8mb4"

engine = create_engine(DATABASE_URL)

def extreme_fix():
    print("🚀 Iniciando reparación EXTREMA de codificación...")
    
    with Session(engine) as session:
        # Patrones detectados en capturas
        patterns = [
            ("Naci-|-n", "Nación"),
            ("Naci||n", "Nación"),
            ("Naci|n", "Nación"),
            ("NaciÂ³n", "Nación"),
            ("NaciÃ³n", "Nación")
        ]
        
        tables = {
            "beneficiarios": "nombre_beneficiario",
            "lista_cuentas": "nombre_cuenta",
            "categorias": "nombre_categoria"
        }
        
        for table, col in tables.items():
            print(f"🔧 Procesando {table}...")
            for bad, good in patterns:
                sql = f"UPDATE {table} SET {col} = REPLACE({col}, '{bad}', '{good}') WHERE {col} LIKE '%{bad}%'"
                res = session.exec(text(sql))
                session.commit()
                # print(f"   -> {bad} a {good} aplicado.")

    print("🏁 Fin de la reparación extrema.")

if __name__ == "__main__":
    extreme_fix()
