import os
import sys

# Desactivar advertencias de decodificación si es posible
os.environ["PYTHONIOENCODING"] = "utf-8"

from sqlmodel import Session, select, create_engine
from passlib.context import CryptContext
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env")))

db_url = os.getenv("DATABASE_URL")
if db_url and "@db:" in db_url:
    db_url = db_url.replace("@db:", "@localhost:")

# Path al backend
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def crear_admin():
    print("--- 3F EMERGENCY AUTH GATE ---")
    
    # Crear un motor local para evitar problemas de sesión global si los hubiera
    engine = create_engine(db_url)
    
    try:
        with Session(engine) as session:
            # Buscar si ya existe el admin
            query = select(User).where(User.email == "admin@3f.com")
            existente = session.exec(query).first()
            
            if existente:
                print("UPDATE: admin@3f.com")
                admin = existente
            else:
                print("CREATE: admin@3f.com")
                admin = User(email="admin@3f.com")
            
            admin.hashed_password = pwd_context.hash("Fer2026!")
            admin.is_active = True
            admin.is_admin = True
            admin.full_name = "Administrador"
            session.add(admin)
            session.commit()
            
            print("USER_CREATED_SUCCESSFULLY")
            
    except Exception as e:
        # Imprimir solo el mensaje de error para evitar caracteres extraños en el dump
        print(f"FAILED: {e.__class__.__name__}")

if __name__ == "__main__":
    crear_admin()
