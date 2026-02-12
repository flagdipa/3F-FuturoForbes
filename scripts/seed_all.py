from backend.core.database import engine, init_db
from backend.models.models import Usuario, Divisa, TipoEntidadFinanciera
from backend.core.auth_utils import get_password_hash
from sqlmodel import Session, select
from datetime import datetime

def seed_everything():
    # 1. Initialize Tables
    print("🚀 Inicializando tablas en 3f_db...")
    init_db()
    
    with Session(engine) as session:
        # 2. Seed Divisas
        print("💱 Poblando divisas...")
        divisas = [
            {"nombre_divisa": "Peso Argentino", "codigo_iso": "ARS", "simbolo_prefijo": "$", "tipo_divisa": "Fiat"},
            {"nombre_divisa": "Dólar Estadounidense", "codigo_iso": "USD", "simbolo_prefijo": "u$d", "tipo_divisa": "Fiat"},
            {"nombre_divisa": "Bitcoin", "codigo_iso": "BTC", "simbolo_prefijo": "₿", "tipo_divisa": "Crypto"},
            {"nombre_divisa": "Ethereum", "codigo_iso": "ETH", "simbolo_prefijo": "Ξ", "tipo_divisa": "Crypto"},
        ]
        for d in divisas:
            existing = session.exec(select(Divisa).where(Divisa.codigo_iso == d["codigo_iso"])).first()
            if not existing:
                session.add(Divisa(**d))
        
        # 3. Seed Default User
        print("👤 Creando usuario administrador...")
        user_email = "fer@forbes.com"
        existing_user = session.exec(select(Usuario).where(Usuario.email == user_email)).first()
        if not existing_user:
            hashed_pw = get_password_hash("password")
            admin = Usuario(
                email=user_email,
                password=hashed_pw,
                creado_el=datetime.now(),
                actualizado_el=datetime.now(),
                bloqueado=False,
                rol_id=1,
                theme_preference="dark"
            )
            session.add(admin)
        
        # 4. Seed Entity Types
        print("🏦 Poblando tipos de entidades financieras...")
        default_types = [
            {"nombre_tipo": "Banco", "descripcion": "Entidad bancaria tradicional", "icono": "fa-university", "color": "#0d6efd"},
            {"nombre_tipo": "Broker", "descripcion": "Agente de bolsa / Sociedad de bolsa", "icono": "fa-chart-line", "color": "#198754"},
            {"nombre_tipo": "Fintech", "descripcion": "Empresa de tecnología financiera", "icono": "fa-mobile-alt", "color": "#6f42c1"},
            {"nombre_tipo": "Billetera Virtual", "descripcion": "Billetera digital / E-wallet", "icono": "fa-wallet", "color": "#fd7e14"},
            {"nombre_tipo": "Exchange Crypto", "descripcion": "Exchange de criptomonedas", "icono": "fa-bitcoin", "color": "#f7931a"},
            {"nombre_tipo": "Otro", "descripcion": "Otro tipo de entidad financiera", "icono": "fa-building", "color": "#6c757d"},
        ]
        for t in default_types:
            existing = session.exec(select(TipoEntidadFinanciera).where(TipoEntidadFinanciera.nombre_tipo == t["nombre_tipo"])).first()
            if not existing:
                session.add(TipoEntidadFinanciera(**t))
        
        session.commit()
        print("✅ Seed completado con éxito.")

if __name__ == "__main__":
    seed_everything()
