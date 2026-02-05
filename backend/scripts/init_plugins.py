import sys
import os

# Add the parent directory to sys.path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlmodel import Session, select
from backend.core.database import engine, init_db
from backend.models.models_plugins import Plugin
from backend.models import * # Ensure all models are loaded

def init_plugins():
    # Construct tables if they don't exist
    init_db()
    
    with Session(engine) as session:
        # Check if plugin exists
        statement = select(Plugin).where(Plugin.nombre_tecnico == "ia_forecasting")
        results = session.exec(statement)
        plugin = results.first()

        if not plugin:
            print("Registering 'ia_forecasting' plugin...")
            new_plugin = Plugin(
                nombre_tecnico="ia_forecasting",
                nombre_display="IA Forecasting Service",
                descripcion="Proyecciones financieras y análisis de tendencias basado en regresión lineal.",
                version="1.0.0",
                autor="3F Core",
                instalado=True,
                activo=True,
                configuracion={"model": "linear_regression", "days_projection": 30},
                hooks_suscritos="dashboard_charts"
            )
            session.add(new_plugin)
            session.commit()
            print("Plugin registered successfully.")
        else:
            print("Plugin 'ia_forecasting' already exists.")
            if not plugin.activo:
                 print("Activating plugin...")
                 plugin.activo = True
                 session.add(plugin)
                 session.commit()
                 print("Plugin activated.")

if __name__ == "__main__":
    init_plugins()
