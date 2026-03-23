import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from backend.models import Account, User, Currency, AccountType
from backend.api.auth.deps import get_current_user
from backend.main import app

def test_create_account(client: TestClient, session: Session):
    # 1. Prerrequisites
    user = User(email="acc@example.com", hashed_password="hash", is_active=True, is_admin=False)
    session.add(user)
    currency = Currency(code="USD", name="Dollar")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)

    # Mock auth
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override

    # 2. POST - now includes 'code' field (required in AccountCreate V2)
    acc_data = {
        "name": "Savings Account",
        "code": "SAVINGS01",
        "type": "ASSET",
        "currency_code": "USD",
        "initial_balance": "1000.00",
        "notes": "My savings"
    }
    
    response = client.post("/api/v1/accounts/", json=acc_data)
    
    # 3. Assertions
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Savings Account"
    assert data["code"] == "SAVINGS01"
    assert float(data["current_balance"]) == 1000.00
    
    # Verify in DB
    db_acc = session.exec(select(Account).where(Account.name == "Savings Account")).first()
    assert db_acc is not None
    assert db_acc.user_id == user.id
    
    app.dependency_overrides.clear()

def test_list_accounts(client: TestClient, session: Session):
    user = User(email="list_acc@example.com", hashed_password="hash", is_active=True, is_admin=False)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    
    for i in range(3):
        acc = Account(
            user_id=user.id,
            name=f"Account {i}",
            code=f"ACC{i:03d}",
            type="ASSET",
            currency_code="ARS",
            initial_balance=0,
            current_balance=0
        )
        session.add(acc)
    session.commit()

    # Mock auth
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override

    response = client.get("/api/v1/accounts/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    
    app.dependency_overrides.clear()

def test_get_account_by_id(client: TestClient, session: Session):
    user = User(email="get_acc@example.com", hashed_password="hash", is_active=True, is_admin=False)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)

    acc = Account(
        user_id=user.id,
        name="Get Test Acc",
        code="GETTEST1",
        type="ASSET",
        currency_code="ARS",
        initial_balance=500,
        current_balance=500
    )
    session.add(acc)
    session.commit()
    session.refresh(acc)

    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override

    response = client.get(f"/api/v1/accounts/{acc.id}")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Get Test Acc"
    assert data["code"] == "GETTEST1"

    app.dependency_overrides.clear()
