from sqlmodel import Session, select
from core.database import engine
from models.models import Usuario, Divisa, ListaCuentas, Categoria, Beneficiario, LibroTransacciones
from core.security import get_password_hash
from datetime import datetime
import decimal

def poblar_datos_prueba():
    with Session(engine) as session:
        # 1. Usuario
        user = session.exec(select(Usuario).where(Usuario.email == "fer@3f.com")).first()
        if not user:
            user = Usuario(email="fer@3f.com", password=get_password_hash("admin123"))
            session.add(user)
        
        # 2. Divisas
        divisa_ars = session.exec(select(Divisa).where(Divisa.codigo_iso == "ARS")).first()
        if not divisa_ars:
            divisa_ars = Divisa(nombre_divisa="Peso Argentino", codigo_iso="ARS", simbolo_prefijo="$", tipo_divisa="Fiat")
            session.add(divisa_ars)
        
        divisa_usd = session.exec(select(Divisa).where(Divisa.codigo_iso == "USD")).first()
        if not divisa_usd:
            divisa_usd = Divisa(nombre_divisa="Dólar Estadounidense", codigo_iso="USD", simbolo_prefijo="U$S", tipo_divisa="Fiat")
            session.add(divisa_usd)
        
        session.commit()
        session.refresh(divisa_ars)
        
        # 3. Categorías
        cat_gastos = session.exec(select(Categoria).where(Categoria.nombre_categoria == "Gastos")).first()
        if not cat_gastos:
            cat_gastos = Categoria(nombre_categoria="Gastos", color="#FF3131")
            session.add(cat_gastos)
            session.commit()
            session.refresh(cat_gastos)
            
            cat_comida = Categoria(nombre_categoria="Comida", id_padre=cat_gastos.id_categoria, color="#FFD700")
            session.add(cat_comida)
        
        # 4. Cuentas
        cuenta = session.exec(select(ListaCuentas).where(ListaCuentas.nombre_cuenta == "Billetera")).first()
        if not cuenta:
            cuenta = ListaCuentas(
                nombre_cuenta="Billetera", 
                tipo_cuenta="Efectivo", 
                saldo_inicial=decimal.Decimal("50000.00"),
                id_divisa=divisa_ars.id_divisa
            )
            session.add(cuenta)
        
        session.commit()
        print("✅ Datos de prueba insertados con éxito.")

if __name__ == "__main__":
    poblar_datos_prueba()
