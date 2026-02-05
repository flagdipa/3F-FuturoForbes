import sys
import os

# Añadir el directorio raíz al path para poder importar los módulos del backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlmodel import SQLModel, create_engine
from backend.core.config import settings
from backend.models.models_notifications import UserNotification
from backend.models.models import Usuario

def create_notifications_table():
    engine = create_engine(settings.DATABASE_URL)
    print(f"Connecting to database to create notifications table...")
    
    try:
        # SQLModel will only create tables that don't exist
        SQLModel.metadata.create_all(engine, tables=[UserNotification.__table__])
        print("✅ Table 'user_notifications' created or already exists!")
    except Exception as e:
        print(f"❌ Error creating table: {e}")

if __name__ == "__main__":
    create_notifications_table()
