import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from backend.main import app
from backend.core.database import get_session

@pytest.fixture(name="session")
def session_fixture():
    # Create an in-memory SQLite database for each test
    engine = create_engine(
        "sqlite://", 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    # Import all models to ensure they are registered with SQLModel metadata
    from backend.models import models, models_config, models_extended, models_advanced, models_plugins
    from backend.models import models_audit # Explicitly import audit models
    
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    # Override the get_session dependency to use our test session
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()
