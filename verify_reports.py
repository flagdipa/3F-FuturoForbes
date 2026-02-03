import sys
import os
from decimal import Decimal
from datetime import datetime

# Set up path
sys.path.append(os.getcwd())

from sqlmodel import select, func
from backend.core.database import get_session
from backend.models.models import LibroTransacciones

def verify_monthly_reports(year: int):
    print(f"Verifying reports for Year: {year}")
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # 1. Calculate Expected Income (Ingresos)
        # Assuming Positive Amount = Income based on router logic
        # OR router uses codigo_transaccion? 
        # Router logic:
        # ingresos_query = select(...).where(..., LibroTransacciones.monto_transaccion > 0)
        
        expected_income = session.exec(
            select(func.sum(LibroTransacciones.monto_transaccion))
            .where(func.extract('year', LibroTransacciones.fecha_transaccion) == year)
            .where(LibroTransacciones.monto_transaccion > 0)
        ).first() or Decimal(0)
        
        # 2. Calculate Expected Expenses (Gastos)
        # Router logic: monto_transaccion < 0
        expected_expenses = session.exec(
            select(func.sum(LibroTransacciones.monto_transaccion))
            .where(func.extract('year', LibroTransacciones.fecha_transaccion) == year)
            .where(LibroTransacciones.monto_transaccion < 0)
        ).first() or Decimal(0)
        
        print(f"Total Logic (DB Sum):")
        print(f"  Ingresos: {expected_income}")
        print(f"  Gastos:   {expected_expenses}")
        print(f"  Neto:     {expected_income + expected_expenses}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    verify_monthly_reports(2026)
