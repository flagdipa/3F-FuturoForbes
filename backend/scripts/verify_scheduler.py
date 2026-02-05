import sys
import os
from datetime import date, datetime
from decimal import Decimal

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlmodel import Session, select
from backend.core.database import engine
from backend.models.models_advanced import TransaccionRecurrente
from backend.models.models import LibroTransacciones, Beneficiario, ListaCuentas
from backend.core.scheduler import check_recurring_transactions

def verify_scheduler():
    with Session(engine) as session:
        print("--- Setting up Test Data ---")
        
        # 1. Ensure Dependencies
        ben = session.exec(select(Beneficiario).where(Beneficiario.nombre_beneficiario == "SchedulerTestBen")).first()
        if not ben:
            ben = Beneficiario(nombre_beneficiario="SchedulerTestBen")
            session.add(ben)
            session.commit()
            session.refresh(ben)
            
        acc = session.exec(select(ListaCuentas)).first()
        if not acc:
            print("No accounts found. Create an account first.")
            return

        # 2. Create an "Auto" Recurring Transaction (Due Yesterday)
        auto_tx = TransaccionRecurrente(
            id_cuenta=acc.id_cuenta,
            id_beneficiario=ben.id_beneficiario,
            codigo_transaccion="Withdrawal",
            monto_transaccion=Decimal(100.00),
            frecuencia="Daily",
            intervalo=1,
            fecha_inicio=date.today(),
            proxima_fecha=date.today(), # Due Today
            activo=1,
            auto_execute=True,
            notas="Auto Execute Test"
        )
        session.add(auto_tx)
        session.flush()
        session.refresh(auto_tx)
        auto_id = auto_tx.id_recurrencia
        print(f"Created Auto-Execute Schedule ID: {auto_id}")

        # 3. Create a "Manual" Recurring Transaction (Due Yesterday)
        manual_tx = TransaccionRecurrente(
            id_cuenta=acc.id_cuenta,
            id_beneficiario=ben.id_beneficiario,
            codigo_transaccion="Withdrawal",
            monto_transaccion=Decimal(200.00),
            frecuencia="Daily",
            intervalo=1,
            fecha_inicio=date.today(),
            proxima_fecha=date.today(), # Due Today
            activo=1,
            auto_execute=False,
            notas="Manual Execute Test"
        )
        session.add(manual_tx)
        session.commit()
        session.refresh(manual_tx)
        manual_id = manual_tx.id_recurrencia
        print(f"Created Manual-Execute Schedule ID: {manual_id}")

    print("\n--- Running Scheduler Check (Simulated) ---")
    try:
        check_recurring_transactions()
        print("Scheduler check completed successfully.")
    except Exception as e:
        print(f"Scheduler execution failed: {e}")
        return

    print("\n--- Verifying Results ---")
    with Session(engine) as session:
        # Check Auto Transaction
        # Should have moved to tomorrow (interval 1 day)
        r_auto = session.get(TransaccionRecurrente, auto_id)
        if r_auto.proxima_fecha > date.today():
             print(f"SUCCESS: Auto ID {r_auto.id_recurrencia} proxima_fecha updated to {r_auto.proxima_fecha}")
        else:
             print(f"FAIL: Auto ID {r_auto.id_recurrencia} was NOT executed. Date: {r_auto.proxima_fecha}")

        # Check Manual Transaction
        # Should NOT have moved
        r_manual = session.get(TransaccionRecurrente, manual_id)
        if r_manual.proxima_fecha == date.today():
             print(f"SUCCESS: Manual ID {r_manual.id_recurrencia} skipped as expected. Date: {r_manual.proxima_fecha}")
        else:
             print(f"FAIL: Manual ID {r_manual.id_recurrencia} was executed incorrectly! Date: {r_manual.proxima_fecha}")

        # Clean up test data
        print("\n--- Cleaning Up ---")
        session.delete(r_auto)
        session.delete(r_manual)
        
        # Delete generated transaction if any (harder to find perfectly without rel, but good enough for now)
        # Assuming last transaction was the one we just made
        last_tx = session.exec(select(LibroTransacciones).order_by(LibroTransacciones.id_transaccion.desc())).first()
        if last_tx and "Auto Execute Test" in (last_tx.notas or ""):
             session.delete(last_tx)
             print("Cleaned up generated transaction.")
        
        session.commit()

if __name__ == "__main__":
    verify_scheduler()
