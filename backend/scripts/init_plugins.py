import sys
import os

# Add the parent directory to sys.path to resolve imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlmodel import Session, select
from backend.core.database import engine, init_db
from backend.models import Plugin
from backend.models import * # Ensure all models are loaded

def init_plugins():
    # Construct tables if they don't exist
    init_db()
    
    with Session(engine) as session:
        # Check if plugin exists
        statement = select(Plugin).where(Plugin.technical_name == "ia_forecasting")
        results = session.exec(statement)
        plugin = results.first()

        if not plugin:
            print("Registering 'ia_forecasting' plugin...")
            new_plugin = Plugin(
                technical_name="ia_forecasting",
                display_name="IA Forecasting Service",
                descripcion="Proyecciones financieras y análisis de tendencias basado en regresión lineal.",
                version="1.0.0",
                autor="3F Core",
                instalado=True,
                is_active=True,
                config={"model": "linear_regression", "days_projection": 30},
                hooks_suscritos="dashboard_charts"
            )
            session.add(new_plugin)
            session.commit()
            print("Plugin registered successfully.")
        # 2. IA OCR
        statement_ocr = select(Plugin).where(Plugin.technical_name == "ia_ocr")
        results_ocr = session.exec(statement_ocr)
        plugin_ocr = results_ocr.first()

        if not plugin_ocr:
            print("Registering 'ia_ocr' plugin...")
            new_ocr = Plugin(
                technical_name="ia_ocr",
                display_name="IA OCR Vision",
                descripcion="Extracción inteligente de datos de facturas y tickets mediante Computer Vision.",
                version="1.0.2",
                autor="3F Core",
                instalado=True,
                is_active=True,
                config={"provider": "google_genai", "confidence_threshold": 0.8},
                hooks_suscritos="vault_upload"
            )
            session.add(new_ocr)
            print("Plugin OCR registered.")

        # 3. Export Tools (Utility)
        statement_exp = select(Plugin).where(Plugin.technical_name == "export_tools")
        results_exp = session.exec(statement_exp)
        plugin_exp = results_exp.first()

        if not plugin_exp:
            print("Registering 'export_tools' plugin...")
            new_exp = Plugin(
                technical_name="export_tools",
                display_name="Export Tools HQ",
                descripcion="Exportación avanzada a Excel, PDF y formatos contables MMEX.",
                version="1.0.0",
                autor="3F Core",
                instalado=True,
                is_active=False,
                config={"default_format": "xlsx"},
                hooks_suscritos="reports_view"
            )
            session.add(new_exp)
            print("Plugin Export registered.")

        session.commit()

if __name__ == "__main__":
    init_plugins()
