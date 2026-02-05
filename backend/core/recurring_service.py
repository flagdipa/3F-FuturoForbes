from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlmodel import Session, select
from backend.models.models_advanced import TransaccionRecurrente
from backend.models.models import LibroTransacciones

class RecurringService:
    def calculate_next_date(self, current_date: date, frequency: str, interval: int) -> date:
        """Helper to calculate next execution date based on frequency"""
        freq = frequency.lower()
        if freq == "daily":
            return current_date + timedelta(days=interval)
        elif freq == "weekly":
            return current_date + timedelta(weeks=interval)
        elif freq == "monthly":
            return current_date + relativedelta(months=interval)
        elif freq == "yearly":
            return current_date + relativedelta(years=interval)
        return current_date

    def execute_recurring(self, session: Session, recurring_id: int) -> dict:
        """
        Executes a specific recurring transaction logic.
        Creates a real transaction and updates the schedule.
        """
        recurring = session.get(TransaccionRecurrente, recurring_id)
        if not recurring:
            raise ValueError("Programación no encontrada")
        
        if recurring.activo == 0:
            raise ValueError("La programación está inactiva")

        # 1. Create the real transaction
        transaction = LibroTransacciones(
            id_cuenta=recurring.id_cuenta,
            id_cuenta_destino=recurring.id_cuenta_destino,
            id_beneficiario=recurring.id_beneficiario,
            codigo_transaccion=recurring.codigo_transaccion,
            monto_transaccion=recurring.monto_transaccion,
            id_categoria=recurring.id_categoria,
            notas=f"[Recurrente] {recurring.notas or ''}",
            fecha_transaccion=str(recurring.proxima_fecha)
        )
        session.add(transaction)
        
        # 2. Update recurring schedule
        recurring.ejecuciones_realizadas += 1
        
        # Calculate next proxima_fecha
        recurring.proxima_fecha = self.calculate_next_date(
            recurring.proxima_fecha, 
            recurring.frecuencia, 
            recurring.intervalo
        )
        
        # Check limits
        if recurring.limite_ejecuciones != -1 and recurring.ejecuciones_realizadas >= recurring.limite_ejecuciones:
            recurring.activo = 0
            
        if recurring.fecha_fin and recurring.proxima_fecha > recurring.fecha_fin:
            recurring.activo = 0
            
        session.add(recurring)
        session.commit()
        
        return {
            "status": "success", 
            "transaction_id": transaction.id_transaccion,
            "next_date": str(recurring.proxima_fecha)
        }

recurring_service = RecurringService()
