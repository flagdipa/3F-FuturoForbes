"""
Instalador de base de datos para el wizard de instalación de 3F
"""
from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from typing import Dict, Optional
import bcrypt
from datetime import datetime
import sys
import os
from decimal import Decimal

# Agregar el directorio raíz del proyecto al path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.models.models import Usuario, Divisa, Categoria


def test_connection(db_type: str, host: str, port: int, user: str, password: str, database: Optional[str] = None) -> Dict[str, any]:
    try:
        if db_type.lower() == "mysql":
            connection_url = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database if database else ''}"
        elif db_type.lower() == "postgresql":
            connection_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database if database else 'postgres'}"
        else:
            return {"success": False, "message": f"Unsupported DB: {db_type}"}
        
        engine = create_engine(connection_url, echo=False)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"success": True, "message": "Connection successful", "connection_url": connection_url}
    except Exception as e:
        return {"success": False, "message": str(e)}


def create_database_if_not_exists(db_type: str, host: str, port: int, user: str, password: str, database: str) -> Dict[str, any]:
    try:
        if db_type.lower() == "mysql":
            url = f"mysql+pymysql://{user}:{password}@{host}:{port}"
            sql = f"CREATE DATABASE IF NOT EXISTS `{database}` CHARACTER SET utf8mb4"
        else:
            url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/postgres"
            sql = f"CREATE DATABASE {database}"
        
        engine = create_engine(url, echo=False)
        with engine.connect() as conn:
            if db_type.lower() == "postgresql":
                res = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{database}'"))
                if res.fetchone(): return {"success": True, "created": False}
            conn.execute(text(sql))
            conn.commit()
        return {"success": True, "created": True}
    except Exception as e:
        if "already exists" in str(e): return {"success": True, "created": False}
        return {"success": False, "message": str(e)}


def run_migrations(connection_url: str) -> Dict[str, any]:
    try:
        engine = create_engine(connection_url)
        SQLModel.metadata.create_all(engine)
        return {"success": True, "message": "Tables created"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def insert_initial_data(connection_url: str) -> Dict[str, any]:
    try:
        engine = create_engine(connection_url)
        with Session(engine) as session:
            if session.exec(select(Divisa)).first():
                return {"success": True, "inserted": False}
            
            divisas = [
                Divisa(nombre_divisa="Peso Argentino", codigo_iso="ARS", simbolo_prefijo="$", decimal_places=2, tipo_divisa="Fiat", tasa_conversion_base=Decimal("1.0")),
                Divisa(nombre_divisa="Dólar", codigo_iso="USD", simbolo_prefijo="US$", decimal_places=2, tipo_divisa="Fiat", tasa_conversion_base=Decimal("1000.0"))
            ]
            for d in divisas: session.add(d)
            
            cats = [
                Categoria(nombre_categoria="Salario", activo=1, color="#00ff9f"),
                Categoria(nombre_categoria="Alimentación", activo=1, color="#ff4444")
            ]
            for c in cats: session.add(c)
            session.commit()
        return {"success": True, "inserted": True}
    except Exception as e:
        return {"success": False, "message": str(e)}


def create_admin_user(connection_url: str, username: str, email: str, password: str, nombre_completo: Optional[str] = None) -> Dict[str, any]:
    try:
        engine = create_engine(connection_url)
        with Session(engine) as session:
            if session.exec(select(Usuario).where(Usuario.email == email)).first():
                return {"success": False, "message": "Email already registered"}
            
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            parts = (nombre_completo or username).split(' ', 1)
            admin = Usuario(
                email=email, password=hashed, nombre=parts[0], 
                apellido=parts[1] if len(parts)>1 else None,
                rol_id=1, theme_preference="dark_neon"
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)
        return {"success": True, "user_id": admin.id_usuario}
    except Exception as e:
        return {"success": False, "message": str(e)}
