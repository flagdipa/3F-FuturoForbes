from backend.core.database import engine
from sqlalchemy import text
import sys

def update_schema():
    with engine.connect() as conn:
        print("Verificando tabla lista_cuentas...")
        try:
            conn.execute(text("ALTER TABLE lista_cuentas ADD COLUMN id_identidad_financiera INT NULL"))
            conn.commit()
            print("✅ Columna id_identidad_financiera agregada.")
        except Exception as e:
            if "Duplicate column name" in str(e):
                print("ℹ️ Columna ya existe.")
            else:
                print(f"❌ Error agregando columna: {e}")

        try:
            conn.execute(text("ALTER TABLE lista_cuentas ADD CONSTRAINT fk_identidad_fin FOREIGN KEY (id_identidad_financiera) REFERENCES identidades_financieras(id_identidad)"))
            conn.commit()
            print("✅ Restricción FK agregada.")
        except Exception as e:
            if "Duplicate key name" in str(e) or "already exists" in str(e).lower():
                print("ℹ️ FK ya existe.")
            else:
                print(f"❌ Error agregando FK: {e}")

if __name__ == "__main__":
    update_schema()
