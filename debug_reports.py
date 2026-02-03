from sqlmodel import Session, select, func, create_engine
from backend.models.models import LibroTransacciones
from backend.core.config import settings
from datetime import datetime

# Setup DB connection
engine = create_engine(settings.DATABASE_URL)

def test_reports():
    with Session(engine) as session:
        current_year = 2026 # Force 2026 based on user screenshot
        print(f"--- TESTING REPORT QUERY FOR YEAR {current_year} ---")
        
        # Test 1: Check if any transactions exist
        count = session.exec(select(func.count()).select_from(LibroTransacciones)).one()
        print(f"Total Transactions in DB: {count}")
        
        # Test 2: Check transactions in 2026
        txs_2026 = session.exec(select(LibroTransacciones).where(func.extract('year', LibroTransacciones.fecha_transaccion) == current_year)).all()
        print(f"Transactions found for {current_year}: {len(txs_2026)}")
        if len(txs_2026) > 0:
            print(f"Sample date: {txs_2026[0].fecha_transaccion}")
        
        # Test 3: Run the exact aggregation query
        ingresos_query = select(
            func.extract('month', LibroTransacciones.fecha_transaccion).label('mes'),
            func.sum(LibroTransacciones.monto_transaccion).label('total')
        ).where(
            func.extract('year', LibroTransacciones.fecha_transaccion) == current_year,
            LibroTransacciones.monto_transaccion > 0
        ).group_by(func.extract('month', LibroTransacciones.fecha_transaccion))
        
        try:
            ingresos = session.exec(ingresos_query).all()
            print("\nIngresos Integrados (Mes, Total):")
            for row in ingresos:
                print(row)
        except Exception as e:
            print(f"\nERROR in Aggregation Query: {e}")

if __name__ == "__main__":
    test_reports()
