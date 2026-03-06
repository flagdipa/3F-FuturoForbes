import sys
import os

# Ensure backend gets added to path to resolve imports correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlmodel import SQLModel
from core.database import engine
from models import metadata_models

def init_db():
    print("Creando tablas según el modelo de datos unificado...")
    SQLModel.metadata.create_all(engine)
    print("¡Tablas creadas de manera exitosa en el nuevo esquema v2!")

if __name__ == "__main__":
    init_db()
