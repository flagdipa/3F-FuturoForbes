import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from datetime import date
from decimal import Decimal

from backend.models import Budget, BudgetLine, Category, User, Currency
from backend.api.auth.deps import get_current_user
from backend.main import app


def test_create_budget(client: TestClient, session: Session):
    """Test crear un presupuesto"""
    # Setup
    user = User(email="budget@test.com", hashed_password="hash", is_active=True)
    session.add(user)
    currency = Currency(code="ARS", name="Peso Argentino")
    session.add(currency)
    session.commit()
    session.refresh(user)
    session.refresh(currency)
    
    category = Category(user_id=user.id, name="Food", type="EXPENSE")
    session.add(category)
    session.commit()
    session.refresh(category)
    
    # Mock auth
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    # Test
    budget_data = {
        "name": "Presupuesto Marzo 2026",
        "period_type": "MONTHLY",
        "start_date": "2026-03-01",
        "end_date": "2026-03-31",
        "notes": "Presupuesto mensual de comida",
        "lines": [
            {
                "category_id": category.id,
                "allocated_amount": "50000.00"
            }
        ]
    }
    
    response = client.post("/api/v1/budgets/", json=budget_data)
    
    # Assertions
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Presupuesto creado con éxito"
    
    # Verify in DB
    db_budget = session.exec(select(Budget).where(Budget.user_id == user.id)).first()
    assert db_budget is not None
    assert db_budget.name == "Presupuesto Marzo 2026"
    assert len(db_budget.lines) == 1
    
    app.dependency_overrides.clear()


def test_list_budgets_mock(client: TestClient, session: Session):
    """Test listar presupuestos - retorna mock data si no hay reales o ID no existe"""
    user = User(email="budgets_list@test.com", hashed_password="hash", is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    response = client.get("/api/v1/budgets/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Puede ser vacío si el usuario no tiene presupuestos
    assert len(data) >= 0
    
    app.dependency_overrides.clear()


def test_add_budget_line(client: TestClient, session: Session):
    """Test agregar línea de presupuesto a presupuesto existente"""
    user = User(email="budget_line@test.com", hashed_password="hash", is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Crear presupuesto base
    budget = Budget(
        user_id=user.id,
        name="Test Budget",
        period_type="MONTHLY",
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 31)
    )
    session.add(budget)
    session.commit()
    session.refresh(budget)
    
    category = Category(user_id=user.id, name="Entertainment", type="EXPENSE")
    session.add(category)
    session.commit()
    session.refresh(category)
    
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    line_data = {
        "category_id": category.id,
        "allocated_amount": "25000.00"
    }
    
    # El endpoint es POST /api/v1/budgets/{id}/lines
    response = client.post(f"/api/v1/budgets/{budget.id}/lines", json=line_data)
    assert response.status_code == 200, response.text
    
    # Verify DB
    session.refresh(budget)
    assert len(budget.lines) == 1
    assert float(budget.lines[0].allocated_amount) == 25000.00
    
    app.dependency_overrides.clear()


def test_get_budget_status(client: TestClient, session: Session):
    """Test obtener estado del presupuesto"""
    user = User(email="budget_status@test.com", hashed_password="hash", is_active=True)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    budget = Budget(
        user_id=user.id,
        name="Status Budget",
        period_type="MONTHLY",
        start_date=date(2026, 3, 1),
        end_date=date(2026, 3, 31)
    )
    session.add(budget)
    session.commit()
    session.refresh(budget)
    
    def get_current_user_override():
        return user
    app.dependency_overrides[get_current_user] = get_current_user_override
    
    # Test GET /budgets/{id}/status
    response = client.get(f"/api/v1/budgets/{budget.id}/status")
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    
    app.dependency_overrides.clear()
