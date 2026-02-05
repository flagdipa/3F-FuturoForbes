import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlmodel import Session, select
from backend.core.database import engine
from backend.models.models_plugins import Plugin

def verify():
    with Session(engine) as session:
        plugin = session.exec(select(Plugin).where(Plugin.nombre_tecnico == "ia_forecasting")).first()
        if plugin:
            print(f"Plugin found: {plugin.nombre_tecnico}")
            print(f"Status: {'Active' if plugin.activo else 'Inactive'}")
            print(f"Config: {plugin.configuracion}")
        else:
            print("Plugin NOT found.")

if __name__ == "__main__":
    verify()
