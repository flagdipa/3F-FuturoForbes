import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

# Importar `app` primero asegura que TODOS los modelos (models.py, models_v2.py,
# models_audit.py, etc.) queden registrados en SQLModel.metadata ANTES de que
# cualquier fixture intente crear las tablas. De esta forma no hay redefiniciones.
from backend.main import app
from backend.core.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """
    Crea una base de datos SQLite in-memory para cada test.
    Todos los modelos ya están registrados en SQLModel.metadata al importar
    backend.main, por lo que NO hay que reimportarlos aquí.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """
    Test client con la sesión de BD en memoria inyectada como dependencia.
    """
    def get_session_override():
        return session

    from backend.dependencies import get_db
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[get_db] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
