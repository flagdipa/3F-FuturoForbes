import sys
import os

# Ensure backend gets added to path to resolve imports correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.database import engine
from sqlmodel import Session, select
from models import Account

def fix_types():
    with Session(engine) as session:
        accounts = session.exec(select(Account)).all()
        for acc in accounts:
            new_type = 'ASSET'
            if acc.type in ['EFECTIVO', 'BANCO', 'BILLETERA_VIRTUAL', 'INVERSION', 'ASSET']:
                new_type = 'ASSET'
            elif acc.type in ['TARJETA_CREDITO', 'PRESTAMO', 'CREDITO', 'LIABILITY']:
                new_type = 'LIABILITY'
            
            if acc.type != new_type:
                acc.type = new_type
                session.add(acc)
        session.commit()
        print("Corrección de tipos de cuenta completada.")

if __name__ == "__main__":
    fix_types()
