from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import Session, select
from datetime import date
from backend.core.database import engine
from backend.models.models import Usuario
from backend.models.models_advanced import TransaccionRecurrente
from backend.core.recurring_service import recurring_service
from backend.core.wealth_service import wealth_service
import logging
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

def check_recurring_transactions():
    """
    Periodic job to check and execute due recurring transactions.
    Only executes those with auto_execute=True.
    """
    logger.info("Running Recurring Transactions Check...")
    today = date.today()
    
    with Session(engine) as session:
        # Find due transactions that are active and set to auto-execute
        query = select(TransaccionRecurrente).where(
            TransaccionRecurrente.activo == 1,
            TransaccionRecurrente.auto_execute == True,
            TransaccionRecurrente.proxima_fecha <= today
        )
        due_transactions = session.exec(query).all()
        
        for tx in due_transactions:
            try:
                logger.info(f"Executing Auto-Recurring Transaction ID: {tx.id_recurrencia}")
                recurring_service.execute_recurring(session, tx.id_recurrencia)
            except Exception as e:
                logger.error(f"Error executing transaction {tx.id_recurrencia}: {e}")

def perform_wealth_snapshots():
    """
    Captures wealth snapshots for all active users.
    """
    logger.info("Capturing Wealth Snapshots...")
    with Session(engine) as session:
        usuarios = session.exec(select(Usuario)).all()
        for u in usuarios:
            try:
                asyncio.run(wealth_service.capture_snapshot(session, u.id_usuario))
            except Exception as e:
                logger.error(f"Error capturing snapshot for user {u.id_usuario}: {e}")

def start_scheduler():
    # Run recurring tx check daily at 00:01
    scheduler.add_job(check_recurring_transactions, 'cron', hour=0, minute=1)
    # Run wealth snapshots daily at 00:05
    scheduler.add_job(perform_wealth_snapshots, 'cron', hour=0, minute=5)
    # Also run once on startup for debugging/missed checks (optional, good for dev)
    # scheduler.add_job(check_recurring_transactions, 'date', run_date=datetime.now() + timedelta(seconds=10)) 
    scheduler.start()
