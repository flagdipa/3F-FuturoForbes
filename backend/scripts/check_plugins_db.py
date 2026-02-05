import sys
import os
# Add parent dir to path to allow imports
# __file__ = backend/scripts/check.py
# dirname = backend/scripts
# dirname = backend
# dirname = root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlmodel import Session, select, create_engine
from backend.models.models_plugins import Plugin
from backend.core.config import settings

# Adjust connection string if needed, assuming default from config
# Direct connection for script
DATABASE_URL = "mysql+pymysql://root:Fer21gon@localhost:3306/futuroforbes_db"
engine = create_engine(DATABASE_URL)

def check_plugins():
    with Session(engine) as session:
        statement = select(Plugin)
        plugins = session.exec(statement).all()
        print(f"--- Installed Plugins ({len(plugins)}) ---")
        found_forecasting = False
        for p in plugins:
            status = "ACTIVE" if p.activo else "INACTIVE"
            print(f"[{p.id_plugin}] {p.nombre_display} ({p.nombre_tecnico}) - {status}")
            if p.nombre_tecnico == "ia_forecasting":
                found_forecasting = True
        
        if not found_forecasting:
            print("\nWARNING: 'ia_forecasting' plugin NOT found.")
        else:
            print("\nSUCCESS: 'ia_forecasting' plugin is registered.")

if __name__ == "__main__":
    check_plugins()
