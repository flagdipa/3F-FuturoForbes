import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from decimal import Decimal
from datetime import datetime
from backend.models import Transaction, TransactionSplit, Account, User, Currency, Payee, TransactionStatus
from backend.api.auth.deps import get_current_user
from backend.main import app

def test_create_transaction(client: TestClient, session: Session):
    """Test creating a new transaction via POST /api/v1/transactions/"""
    # 1. Prerrequisites: User, Currency, Account, Payee
    user = User(email="test_tx@example.com", hashed_password="hash", is_active=True, is_admin=False)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)
    
    account = Account(
        user_id=user.id,
        name="Test Account",
        code="TXTEST01",
        type="ASSET",
        currency_code=currency.code,
        current_balance=Decimal("0")
    )
    session.add(account)
    
    payee = Payee(user_id=user.id, name="Test Payee", code="PAYEE001")
    session.add(payee)
    session.commit()
    session.refresh(account)
    session.refresh(payee)

    # Mock authentication
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override

    # 2. POST Request (V2 schema)
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
    
    response = client.post("/api/v1/transactions/", json=tx_data)
    
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

def test_list_transactions(client: TestClient, session: Session):
    """Test listing transactions via GET /api/v1/transactions/"""
    user = User(email="list_tx@example.com", hashed_password="hash", is_active=True, is_admin=False)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)
    
    account = Account(
        user_id=user.id,
        name="List Account",
        code="LISTACC1",
        type="ASSET",
        currency_code="ARS",
        current_balance=Decimal("0")
    )
    session.add(account)
    
    payee = Payee(user_id=user.id, name="List Payee", code="LISTPAY1")
    session.add(payee)
    session.commit()
    session.refresh(account)
    session.refresh(payee)
    
    # Insert 5 transactions directly in DB
    for i in range(5):
        tx = Transaction(
            user_id=user.id,
            payee_id=payee.id,
            date=datetime(2024, 1, i + 1),
            notes=f"TX {i}",
            status=TransactionStatus.PENDING
        )
        session.add(tx)
        session.commit()
        session.refresh(tx)
        
        split = TransactionSplit(
            transaction_id=tx.id,
            account_id=account.id,
            amount=Decimal(100 * (i + 1)),
            currency_code="ARS"
        )
        session.add(split)
        session.commit()
        
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    # Test GET
    response = client.get("/api/v1/transactions/")
    assert response.status_code == 200, response.text
    res_data = response.json()
    
    assert isinstance(res_data, list)
    assert len(res_data) == 5
    
    app.dependency_overrides.pop(get_current_user, None)

def test_void_transaction(client: TestClient, session: Session):
    """Test voiding a transaction via POST /api/v1/transactions/{id}/void"""
    user = User(email="void_tx@example.com", hashed_password="hash", is_active=True, is_admin=False)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)
    
    account = Account(
        user_id=user.id,
        name="Void Account",
        code="VOIDACC1",
        type="ASSET",
        currency_code="ARS",
        current_balance=Decimal("0")
    )
    session.add(account)
    payee = Payee(user_id=user.id, name="Void Payee", code="VOIDPAY1")
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

    # Test VOID
    response = client.post(f"/api/v1/transactions/{tx_id}/void?reason=Test+Void")
    assert response.status_code == 200, response.text
    
    # Verify voided status
    session.refresh(tx)
    db_tx = session.get(Transaction, tx_id)
    assert db_tx.status == TransactionStatus.VOID
    
    app.dependency_overrides.pop(get_current_user, None)
