import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from decimal import Decimal
from datetime import datetime
from backend.models import Transaction, TransactionSplit, Account, User, Currency, Payee, TransactionStatus
from backend.api.auth.deps import get_current_user
from backend.main import app

def test_create_transaction_integration(client: TestClient, session: Session):
    # 1. Prerrequisites: User, Currency, Account, Beneficiary
    # Note: Using V2 models
    user = User(email="test@example.com", hashed_password="hash", is_active=True, is_admin=False)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)
    
    account = Account(user_id=user.id, name="Test Account", type="ASSET", currency_code=currency.code)
    session.add(account)
    
    payee = Payee(user_id=user.id, name="Test Payee")
    session.add(payee)
    session.commit()
    session.refresh(account)
    session.refresh(payee)

    # Mock authentication
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override

    # 2. POST Request (New schema)
    tx_data = {
        "date": "2024-02-05T00:00:00",
        "description": "Integration Test TX",
        "payee_id": payee.id,
        "notes": "Integration Test Notes",
        "splits": [
            {
                "account_id": account.id,
                "amount": "1500.50",
                "currency_code": "ARS"
            }
        ]
    }
    
    response = client.post("/api/transacciones/", json=tx_data)
    
    # 3. Assertions
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["notes"] == "Integration Test Notes"
    assert data["description"] == "Integration Test TX"
    assert len(data["splits"]) == 1
    assert float(data["splits"][0]["amount"]) == 1500.50
    
    # Verify in DB
    db_tx = session.exec(select(Transaction)).first()
    assert db_tx is not None
    assert db_tx.notes == "Integration Test Notes"
    assert len(db_tx.splits) == 1
    assert float(db_tx.splits[0].amount) == 1500.50
    
    # Clean up override
    app.dependency_overrides.pop(get_current_user, None)

def test_list_transactions_paginated(client: TestClient, session: Session):
    user = User(email="list@example.com", hashed_password="hash", is_active=True, is_admin=False)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)
    
    account = Account(user_id=user.id, name="List Account", type="ASSET", currency_code=currency.code)
    session.add(account)
    
    payee = Payee(user_id=user.id, name="List Payee")
    session.add(payee)
    session.commit()
    session.refresh(account)
    session.refresh(payee)
    
    for i in range(10):
        tx = Transaction(
            user_id=user.id,
            payee_id=payee.id,
            date=datetime(2024, 1, 1),
            notes=f"TX {i}",
            status=TransactionStatus.PENDING
        )
        session.add(tx)
        session.commit()
        session.refresh(tx)
        
        split = TransactionSplit(
            transaction_id=tx.id,
            account_id=account.id,
            amount=Decimal(100 * i),
            currency_code="ARS"
        )
        session.add(split)
        session.commit()
        
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    # Test GET
    response = client.get("/api/transacciones/?limit=5&skip=0")
    assert response.status_code == 200, response.text
    res_data = response.json()
    
    # New endpoint returns a list directly
    assert isinstance(res_data, list)
    assert len(res_data) == 5
    
    app.dependency_overrides.pop(get_current_user, None)

def test_void_transaction(client: TestClient, session: Session):
    user = User(email="void@example.com", hashed_password="hash", is_active=True, is_admin=False)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)
    
    account = Account(user_id=user.id, name="Void Account", type="ASSET", currency_code=currency.code)
    session.add(account)
    payee = Payee(user_id=user.id, name="Void Payee")
    session.add(payee)
    session.commit()
    session.refresh(account)
    session.refresh(payee)
    
    tx = Transaction(
        user_id=user.id,
        payee_id=payee.id,
        date=datetime(2024, 1, 1),
        status=TransactionStatus.PENDING
    )
    session.add(tx)
    session.commit()
    session.refresh(tx)
    
    split = TransactionSplit(
        transaction_id=tx.id,
        account_id=account.id,
        amount=Decimal("50.00"),
        currency_code="ARS"
    )
    session.add(split)
    session.commit()
    session.refresh(tx)
    
    tx_id = tx.id

    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override

    # Test VOID instead of DELETE (V2 uses void)
    response = client.post(f"/api/transacciones/{tx_id}/void?reason=Test Void")
    assert response.status_code == 200, response.text
    
    # Verify voided status
    db_tx = session.get(Transaction, tx_id)
    assert db_tx.status == TransactionStatus.VOID
    
    app.dependency_overrides.pop(get_current_user, None)
