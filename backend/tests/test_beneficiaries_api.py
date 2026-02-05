from fastapi.testclient import TestClient
from sqlmodel import Session, select
from backend.models.models import Beneficiario, Categoria, Usuario
from backend.api.auth.deps import get_current_user
import pytest

def test_create_beneficiary_integration(client: TestClient, session: Session):
    # 1. Setup User and Category
    user = Usuario(email="benef_test@example.com", password="hash")
    session.add(user)
    category = Categoria(nombre_categoria="Test Category")
    session.add(category)
    session.commit()
    session.refresh(user)
    session.refresh(category)

    # Mock authentication
    def get_current_user_override():
        return user
    from backend.main import app
    app.dependency_overrides[get_current_user] = get_current_user_override

    # 2. Create beneficiary via API
    beneficiary_data = {
        "nombre_beneficiario": "Test Global Corp",
        "id_categoria": category.id_categoria,
        "cbu": "1234567890",
        "banco": "Test Bank",
        "activo": 1
    }
    
    response = client.post("/api/beneficiarios/", json=beneficiary_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["nombre_beneficiario"] == beneficiary_data["nombre_beneficiario"]
    assert "id_beneficiario" in data

    # 3. Verify in DB
    db_benef = session.get(Beneficiario, data["id_beneficiario"])
    assert db_benef is not None
    assert db_benef.nombre_beneficiario == "Test Global Corp"
    
    # Cleanup overrides
    app.dependency_overrides.clear()

def test_listar_beneficiarios_paginado(client: TestClient, session: Session):
    # 1. Add multiple beneficiaries
    for i in range(5):
        benef = Beneficiario(
            nombre_beneficiario=f"Beneficiary {i}",
            activo=1
        )
        session.add(benef)
    session.commit()

    # 2. Test list with pagination
    response = client.get("/api/beneficiarios/", params={"limit": 2, "offset": 0})
    assert response.status_code == 200
    data = response.json()
    
    assert len(data["data"]) == 2
    assert data["pagination"]["total"] >= 5
    assert data["pagination"]["limit"] == 2
    assert data["pagination"]["has_more"] is True

def test_eliminar_beneficiario_integration(client: TestClient, session: Session):
    # 1. Setup User and Beneficiary
    user = Usuario(email="del_benef@example.com", password="hash")
    session.add(user)
    session.commit()
    session.refresh(user)
    
    benef = Beneficiario(
        nombre_beneficiario="Temp Beneficiary",
        activo=1
    )
    session.add(benef)
    session.commit()
    session.refresh(benef)

    # Mock authentication
    def get_current_user_override():
        return user
    from backend.main import app
    app.dependency_overrides[get_current_user] = get_current_user_override

    # 2. Delete via API
    response = client.delete(f"/api/beneficiarios/{benef.id_beneficiario}")
    assert response.status_code == 200

    # 3. Verify gone
    db_benef = session.get(Beneficiario, benef.id_beneficiario)
    assert db_benef is None
    
    # Cleanup overrides
    app.dependency_overrides.clear()
