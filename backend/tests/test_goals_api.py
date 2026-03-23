import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import date
from decimal import Decimal

from backend.models import SavingGoal, GoalContribution, User, Currency
from backend.api.auth.deps import get_current_user
from backend.main import app


def test_create_goal(client: TestClient, session: Session):
    """Test crear una meta de ahorro"""
    # Setup
    user = User(email="goal@test.com", hashed_password="hash", is_active=True)
    session.add(user)
    currency = Currency(code="ARS", name="Peso Argentino")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)
    
    # Mock auth
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    # Test
    goal_data = {
        "name": "Vacaciones 2026",
        "target_amount": "500000.00",
        "current_amount": "50000.00",
        "target_date": "2026-12-31",
        "currency_code": "ARS",
        "notes": "Ahorro para vacaciones"
    }
    
    response = client.post("/api/v1/goals/", json=goal_data)
    
    # Assertions
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Vacaciones 2026"
    # Convert to float for comparison due to decimal places in DB
    assert float(data["target_amount"]) == 500000.00
    assert float(data["current_amount"]) == 50000.00
    assert data["is_completed"] == False
    
    # Verify in DB
    db_goal = session.exec(select(SavingGoal).where(SavingGoal.user_id == user.id)).first()
    assert db_goal is not None
    assert float(db_goal.target_amount) == 500000.00
    
    app.dependency_overrides.clear()


def test_list_goals(client: TestClient, session: Session):
    """Test listar metas de ahorro del usuario"""
    user = User(email="goals_list@test.com", hashed_password="hash", is_active=True)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    
    # Create test goals
    for i in range(3):
        goal = SavingGoal(
            user_id=user.id,
            name=f"Goal {i}",
            target_amount=Decimal("1000.00"),
            current_amount=Decimal("100.00"),
            currency_code="ARS",
            target_date=date(2026, 12, 31)
        )
        session.add(goal)
    session.commit()
    
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    response = client.get("/api/v1/goals/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    
    app.dependency_overrides.clear()


def test_update_goal(client: TestClient, session: Session):
    """Test actualizar una meta de ahorro"""
    user = User(email="goal_update@test.com", hashed_password="hash", is_active=True)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    
    goal = SavingGoal(
        user_id=user.id,
        name="Viaje",
        target_amount=Decimal("300000.00"),
        current_amount=Decimal("50000.00"),
        currency_code="ARS",
        target_date=date(2026, 6, 30)
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    update_data = {
        "current_amount": "100000.00",
        "notes": "Updated progress"
    }
    response = client.patch(f"/api/v1/goals/{goal.id}", json=update_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert float(data["current_amount"]) == 100000.00
    
    app.dependency_overrides.clear()


def test_contribute_to_goal(client: TestClient, session: Session):
    """Test agregar contribución a una meta"""
    user = User(email="goal_contrib@test.com", hashed_password="hash", is_active=True)
    session.add(user)
    currency = Currency(code="ARS", name="Peso")
    session.add(currency)
    session.commit()
    session.refresh(user)
    
    goal = SavingGoal(
        user_id=user.id,
        name="Fondo Emergencia",
        target_amount=Decimal("1000000.00"),
        current_amount=Decimal("100000.00"),
        currency_code="ARS"
    )
    session.add(goal)
    session.commit()
    session.refresh(goal)
    
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    contrib_data = {"amount": "50000.00"}
    response = client.post(f"/api/v1/goals/{goal.id}/contribute", json=contrib_data)
    assert response.status_code == 200, response.text
    data = response.json()
    assert float(data["current_amount"]) == 150000.00
    
    app.dependency_overrides.clear()
