import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlmodel import create_engine, text
from backend.core.config import settings
from backend.models.models import SQLModel

# Force load models
from backend.models.models import MetaAhorro, Presupuesto

# Create engine (Assuming DATABASE_URL is available in settings or .env)
# Using direct connection string fallback if needed, but trying settings first
try:
    engine = create_engine(settings.DATABASE_URL)
except:
    # Fallback for AppServ/Local environment if settings fails
    engine = create_engine("mysql+pymysql://root:Fer21gon@localhost:3306/futuro_forbes_db")

def run_migration():
    print("Running Schema Fix for Phase 13 & 14...")
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        
        # 1. Add columns to tabla_presupuestos (Phase 14)
        try:
            print("Checking tabla_presupuestos...")
            # Check if column exists
            check_sql = text("SHOW COLUMNS FROM tabla_presupuestos LIKE 'es_rolling'")
            res = conn.execute(check_sql).fetchone()
            if not res:
                print("Adding 'es_rolling' and 'monto_acumulado' to tabla_presupuestos")
                conn.execute(text("ALTER TABLE tabla_presupuestos ADD COLUMN es_rolling TINYINT(1) DEFAULT 0"))
                conn.execute(text("ALTER TABLE tabla_presupuestos ADD COLUMN monto_acumulado DECIMAL(15,2) DEFAULT 0.00"))
            else:
                print("Columns already exist in tabla_presupuestos.")
        except Exception as e:
            print(f"Error updating tabla_presupuestos: {e}")

        # 2. Create metas_ahorro table (Phase 13)
        # Using SQLModel create_all is safer for new tables
        print("Creating new tables (MetaAhorro)...")
        SQLModel.metadata.create_all(engine)
        
    print("Migration completed.")

if __name__ == "__main__":
    run_migration()
