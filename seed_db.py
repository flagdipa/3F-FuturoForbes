"""Script to seed the database with initial user data."""
import sys
import os
sys.path.insert(0, os.getcwd())

from sqlmodel import Session, select
from backend.core.database import engine
from backend.models.models import Usuario, Divisa
from backend.core.auth_utils import get_password_hash

def seed():
    with Session(engine) as session:
        # Usuario principal
        user = session.exec(select(Usuario).where(Usuario.email == "fer@3f.com")).first()
        if not user:
            user = Usuario(
                email="fer@3f.com",
                password=get_password_hash("Fer2026!"),
                nombre="Fer",
                apellido="Forbes"
            )
            session.add(user)
            print("✅ Usuario fer@3f.com creado")
        else:
            # Actualizar password por si acaso
            user.password = get_password_hash("Fer2026!")
            session.add(user)
            print("✅ Usuario fer@3f.com actualizado")

        # Divisas básicas
        ars = session.exec(select(Divisa).where(Divisa.codigo_iso == "ARS")).first()
        if not ars:
            session.add(Divisa(
                nombre_divisa="Peso Argentino", codigo_iso="ARS",
                simbolo_prefijo="$", tipo_divisa="Fiat", decimal_places=2
            ))
            print("✅ Divisa ARS creada")

        usd = session.exec(select(Divisa).where(Divisa.codigo_iso == "USD")).first()
        if not usd:
            session.add(Divisa(
                nombre_divisa="Dólar Estadounidense", codigo_iso="USD",
                simbolo_prefijo="U$S", tipo_divisa="Fiat", decimal_places=2
            ))
            print("✅ Divisa USD creada")

        session.commit()
        print("\n✅ Base de datos inicializada correctamente.")
        print("   Email:      fer@3f.com")
        print("   Contraseña: Fer2026!")

if __name__ == "__main__":
    seed()
