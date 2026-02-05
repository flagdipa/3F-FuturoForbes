import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from backend.models.models import LibroTransacciones, ListaCuentas, Divisa, Usuario, Beneficiario
from backend.api.auth.deps import get_current_user

def test_create_transaction_integration(client: TestClient, session: Session):
    # 1. Prerrequisites: User, Currency, Account, Beneficiary
    user = Usuario(email="test@example.com", password="hash")
    session.add(user)
    divisa = Divisa(nombre_divisa="Peso", codigo_iso="ARS", tipo_divisa="Fiat")
    session.add(divisa)
    session.commit()
    session.refresh(user)
    session.refresh(divisa)
    
    cuenta = ListaCuentas(nombre_cuenta="Test Account", tipo_cuenta="Efectivo", id_divisa=divisa.id_divisa)
    session.add(cuenta)
    
    benef = Beneficiario(nombre_beneficiario="Test Payee")
    session.add(benef)
    session.commit()
    session.refresh(cuenta)
    session.refresh(benef)

    # Mock authentication
    def get_current_user_override():
        return user
    from backend.main import app
    app.dependency_overrides[get_current_user] = get_current_user_override

    # 2. POST Request
    tx_data = {
        "id_cuenta": cuenta.id_cuenta,
        "fecha_transaccion": "2024-02-05T00:00:00",
        "monto_transaccion": 1500.50,
        "id_beneficiario": benef.id_beneficiario,
        "id_categoria": None,
        "notas": "Integration Test TX",
        "codigo_transaccion": "Withdrawal",
        "es_dividida": False,
        "etiquetas": []
    }
    
    response = client.post("/api/transacciones/", json=tx_data)
    
    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    assert float(data["monto_transaccion"]) == 1500.50
    assert data["notas"] == "Integration Test TX"
    
    # Verify in DB
    db_tx = session.exec(select(LibroTransacciones)).first()
    assert db_tx is not None
    assert db_tx.monto_transaccion == 1500.50

def test_list_transactions_paginated(client: TestClient, session: Session):
    # Setup multiple transactions
    divisa = Divisa(nombre_divisa="Peso", codigo_iso="ARS", tipo_divisa="Fiat")
    session.add(divisa)
    session.commit()
    session.refresh(divisa)
    
    cuenta = ListaCuentas(nombre_cuenta="List Account", tipo_cuenta="Efectivo", id_divisa=divisa.id_divisa)
    session.add(cuenta)
    
    benef = Beneficiario(nombre_beneficiario="List Payee")
    session.add(benef)
    session.commit()
    session.refresh(cuenta)
    session.refresh(benef)
    
    for i in range(10):
        tx = LibroTransacciones(
            id_cuenta=cuenta.id_cuenta,
            id_beneficiario=benef.id_beneficiario,
            monto_transaccion=100 * i,
            fecha_transaccion="2024-01-01",
            notas=f"TX {i}",
            codigo_transaccion="Withdrawal",
            es_dividida=False
        )
        session.add(tx)
    session.commit()
    
    # Test GET
    response = client.get("/api/transacciones/?limit=5&offset=0")
    assert response.status_code == 200
    res_data = response.json()
    
    assert len(res_data["data"]) == 5
    assert res_data["pagination"]["total"] == 10
    assert res_data["pagination"]["has_more"] is True

def test_delete_transaction(client: TestClient, session: Session):
    # Setup user and tx
    user = Usuario(email="del@example.com", password="hash")
    session.add(user)
    divisa = Divisa(nombre_divisa="Peso", codigo_iso="ARS", tipo_divisa="Fiat")
    session.add(divisa)
    session.commit()
    session.refresh(user)
    session.refresh(divisa)
    
    cuenta = ListaCuentas(id_divisa=divisa.id_divisa, nombre_cuenta="Del Account", tipo_cuenta="Efectivo")
    session.add(cuenta)
    benef = Beneficiario(nombre_beneficiario="Del Payee")
    session.add(benef)
    session.commit()
    session.refresh(cuenta)
    session.refresh(benef)
    
    tx = LibroTransacciones(
        id_cuenta=cuenta.id_cuenta, 
        id_beneficiario=benef.id_beneficiario,
        monto_transaccion=50, 
        fecha_transaccion="2024-01-01",
        codigo_transaccion="Withdrawal",
        es_dividida=False
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)
    
    tx_id = tx.id_transaccion

    # Mock auth
    from backend.api.auth.deps import get_current_user
    from backend.main import app
    app.dependency_overrides[get_current_user] = lambda: user

    response = client.delete(f"/api/transacciones/{tx_id}")
    assert response.status_code == 200
    
    # Verify deletion
    assert session.get(LibroTransacciones, tx_id) is None
