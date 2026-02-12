from sqlmodel import Session, create_engine, select
from backend.models.models import Presupuesto, Categoria
from backend.models.models_config import AnioPresupuesto
from datetime import datetime
import os
from dotenv import load_dotenv
from decimal import Decimal

# Cargar entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "mysql+pymysql://root:@localhost:3306/3f_db?charset=utf8mb4"

engine = create_engine(DATABASE_URL)

def seed_budget_2026():
    print("🚀 Generando Presupuesto 2026 para pruebas...")
    
    with Session(engine) as session:
        # 1. Crear o recuperar el Año de Presupuesto 2026
        anio_2026 = session.exec(select(AnioPresupuesto).where(AnioPresupuesto.anio == 2026)).first()
        if not anio_2026:
            anio_2026 = AnioPresupuesto(
                anio=2026,
                nombre="Presupuesto Maestro 2026",
                notas="Generado automáticamente para pruebas de Phase 13",
                activo=1,
                fecha_creacion=datetime.now()
            )
            session.add(anio_2026)
            session.commit()
            session.refresh(anio_2026)
            print("   ✅ Año 2026 creado.")
        else:
            print("   ℹ️ Año 2026 ya existe.")

        # 2. Obtener categorías para asignar presupuestos
        # Buscamos algunas categorías comunes
        categorias = session.exec(select(Categoria).limit(10)).all()
        if not categorias:
            print("   ⚠️ No hay categorías en la base de datos! Abortando.")
            return

        print(f"   📊 Asignando montos a {len(categorias)} categorías...")
        
        # Montos de prueba
        montos_test = {
            "Alquiler": 150000,
            "Alimentación": 80000,
            "Servicios": 30000,
            "Internet": 15000,
            "Ocio": 20000,
            "Salario": 500000 # Aunque sea ingreso, MMEX a veces permite presupuestar ingresos
        }

        count = 0
        for cat in categorias:
            # Verificar si ya tiene presupuesto para este año
            existing = session.exec(
                select(Presupuesto).where(
                    Presupuesto.id_anio_presupuesto == anio_2026.id_anio_presupuesto,
                    Presupuesto.id_categoria == cat.id_categoria
                )
            ).first()
            
            if not existing:
                # Asignar monto basado en nombre o default
                monto = montos_test.get(cat.nombre_categoria, 10000)
                
                pres = Presupuesto(
                    id_anio_presupuesto=anio_2026.id_anio_presupuesto,
                    id_categoria=cat.id_categoria,
                    periodo="Monthly",
                    monto=Decimal(monto),
                    activo=1,
                    es_rolling=False
                )
                session.add(pres)
                count += 1
        
        if count > 0:
            session.commit()
            print(f"   ✅ Se crearon {count} entradas de presupuesto para 2026.")
        else:
            print("   ✨ Ya existen entradas de presupuesto para todas las categorías del 2026.")

    print("🏁 Seed de Presupuesto finalizado.")

if __name__ == "__main__":
    seed_budget_2026()
