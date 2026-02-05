import sys
import os
from datetime import datetime
from decimal import Decimal

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from sqlmodel import Session, select
from backend.core.database import engine
from backend.models.models import Presupuesto, Categoria, LibroTransacciones, Beneficiario, ListaCuentas

def create_test_budget():
    with Session(engine) as session:
        # 1. Create a Test Category
        cat = session.exec(select(Categoria).where(Categoria.nombre_categoria == "TestBudget")).first()
        if not cat:
            cat = Categoria(nombre_categoria="TestBudget", tipo="Expense")
            session.add(cat)
            session.commit()
            session.refresh(cat)
            print(f"Category 'TestBudget' created with ID: {cat.id_categoria}")
        
        # 2. Create a Budget for it
        budget = session.exec(select(Presupuesto).where(Presupuesto.id_categoria == cat.id_categoria)).first()
        if not budget:
            budget = Presupuesto(id_categoria=cat.id_categoria, monto=Decimal(10000.00), periodo="Monthly")
            session.add(budget)
            session.commit()
            print("Budget created: Limit $10,000")
        
        # 3. Ensure User/Account/Beneficiary exist
        # We need a Beneficiary
        ben = session.exec(select(Beneficiario).where(Beneficiario.nombre_beneficiario == "TestBeneficiary")).first()
        if not ben:
            ben = Beneficiario(nombre_beneficiario="TestBeneficiary")
            session.add(ben)
            session.commit()
            session.refresh(ben)

        # We need an Account
        acc = session.get(ListaCuentas, 1)
        if not acc:
             # Create a dummy account if ID 1 doesn't exist (though usually it does in this seed)
             # Asking for an account via query to be safe
             acc = session.exec(select(ListaCuentas)).first()
             if not acc:
                 print("Error: No accounts found to assign transaction.")
                 return

        # 4. Create a Transaction to impact the budget
        tx = LibroTransacciones(
            id_cuenta=acc.id_cuenta,
            id_categoria=cat.id_categoria,
            id_beneficiario=ben.id_beneficiario,
            monto_transaccion=Decimal(-5000.00), # Expense
            codigo_transaccion="Withdrawal",
            # pagador_id removed
            fecha_transaccion=datetime.utcnow().strftime("%Y-%m-%d"),
            notas="Test Budget Expense"
        )
        session.add(tx)
        session.commit()
        print("Transaction added: -$5,000")
        
        print(f"Verification Ready. Check /presupuestos. Should see 'TestBudget' at 50% ($5,000/$10,000).")

if __name__ == "__main__":
    try:
        create_test_budget()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
