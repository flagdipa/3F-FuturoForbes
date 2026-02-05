from fastapi.testclient import TestClient
from sqlmodel import Session, select
from backend.models.models import ListaCuentas, Divisa, Usuario
from backend.api.auth.deps import get_current_user
import pytest

def test_create_account_integration(client: TestClient, session: Session):
    # 1. Prerrequisites: User, Currency
    user = Usuario(email="account_test@example.com", password="hash")
    session.add(user)
    currency = Divisa(nombre_divisa="USD_ACC", simbolo_prefijo="$", codigo_iso="USD_A", tipo_divisa="Fiat")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)

    # Mock authentication
    def get_current_user_override():
        return user
    from backend.main import app
    app.dependency_overrides[get_current_user] = get_current_user_override

    # 2. Create account via API
    account_data = {
        "nombre_cuenta": "Test Checking Account",
        "tipo_cuenta": "Checking",
        "id_divisa": currency.id_divisa,
        "saldo_inicial": 1000.00,
        "estado": "Open"
    }
    
    response = client.post("/api/cuentas/", json=account_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["nombre_cuenta"] == account_data["nombre_cuenta"]
    assert "id_cuenta" in data

    # 3. Verify in DB
    db_account = session.get(ListaCuentas, data["id_cuenta"])
    assert db_account is not None
    assert db_account.nombre_cuenta == "Test Checking Account"
    
    # Cleanup overrides
    app.dependency_overrides.clear()

def test_listar_cuentas_paginado(client: TestClient, session: Session):
    # 1. Setup currency
    currency = Divisa(nombre_divisa="EUR_ACC", simbolo_prefijo="€", codigo_iso="EUR_A", tipo_divisa="Fiat")
    session.add(currency)
    session.commit()
    session.refresh(currency)

    # 2. Add multiple accounts
    for i in range(5):
        acc = ListaCuentas(
            nombre_cuenta=f"Paginated Account {i}",
            tipo_cuenta="Checking",
            id_divisa=currency.id_divisa,
            saldo_inicial=100.0 * i
        )
        session.add(acc)
    session.commit()

    # 3. Test list with pagination
    response = client.get("/api/cuentas/", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["data"]) == 2
    assert data["pagination"]["total"] >= 5
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["has_more"] is True

def test_eliminar_cuenta_integration(client: TestClient, session: Session):
    # 1. Setup User and Account
    user = Usuario(email="del_acc@example.com", password="hash")
    session.add(user)
    currency = Divisa(nombre_divisa="GBP_ACC", simbolo_prefijo="£", codigo_iso="GBP_A", tipo_divisa="Fiat")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)
    
    account = ListaCuentas(
        nombre_cuenta="Delete Me Account",
        tipo_cuenta="Savings",
        id_divisa=currency.id_divisa
    )
    session.add(account)
    session.commit()
    session.refresh(account)

    # Mock authentication
    def get_current_user_override():
        return user
    from backend.main import app
    app.dependency_overrides[get_current_user] = get_current_user_override

    # 2. Delete via API
    response = client.delete(f"/api/cuentas/{account.id_cuenta}")
    assert response.status_code == 200

    # 3. Verify gone
    db_account = session.get(ListaCuentas, account.id_cuenta)
    assert db_account is None
    
    # Cleanup overrides
    app.dependency_overrides.clear()
