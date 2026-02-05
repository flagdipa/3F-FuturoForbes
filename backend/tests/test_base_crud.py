import pytest
from sqlmodel import Session, select
from backend.api.base_crud import BaseCRUDService
from backend.models.models import Categoria
from backend.api.categories.schemas import CategoriaCrear
from backend.models.models_audit import AuditLog

def test_base_crud_create(session: Session):
    # Initialize service
    service = BaseCRUDService[Categoria, CategoriaCrear, CategoriaCrear](Categoria)
    
    # Create data
    cat_in = CategoriaCrear(nombre_categoria="Test Category", color="#FFFFFF")
    
    # Perform create with audit context
    db_cat = service.create(session, cat_in, user_id=1, ip_address="127.0.0.1")
    
    # Assertions
    assert db_cat.id_categoria is not None
    assert db_cat.nombre_categoria == "Test Category"
    
    # Verify Audit Log entry was created
    audit = session.exec(select(AuditLog)).all()
    assert len(audit) == 1
    assert audit[0].accion == "CREATE"
    assert audit[0].entidad == "Categoria"
    assert audit[0].id_usuario == 1
    assert audit[0].ip_address == "127.0.0.1"

def test_base_crud_list(session: Session):
    service = BaseCRUDService[Categoria, CategoriaCrear, CategoriaCrear](Categoria)
    
    # Add dummy data directly to session
    for i in range(5):
        cat = Categoria(nombre_categoria=f"Cat {i}")
        session.add(cat)
    session.commit()
    
    # Test list with pagination
    res = service.list(session, limit=2)
    assert len(res.data) == 2
    assert res.pagination.total == 5
    assert res.pagination.has_more is True

def test_base_crud_update(session: Session):
    service = BaseCRUDService[Categoria, CategoriaCrear, CategoriaCrear](Categoria)
    
    # Setup initial record
    cat = Categoria(nombre_categoria="Old Name")
    session.add(cat)
    session.commit()
    session.refresh(cat)
    
    # Update through service
    update_in = CategoriaCrear(nombre_categoria="New Name")
    updated_cat = service.update(session, cat, update_in, user_id=99)
    
    assert updated_cat.nombre_categoria == "New Name"
    
    # Verify Audit trail for UPDATE
    audit = session.exec(select(AuditLog).where(AuditLog.accion == "UPDATE")).first()
    assert audit is not None
    assert audit.id_usuario == 99
    assert audit.entidad == "Categoria"

def test_base_crud_delete(session: Session):
    service = BaseCRUDService[Categoria, CategoriaCrear, CategoriaCrear](Categoria)
    
    # Setup record
    cat = Categoria(nombre_categoria="To Delete")
    session.add(cat)
    session.commit()
    session.refresh(cat)
    
    id_to_del = cat.id_categoria
    
    # Delete through service
    success = service.delete(session, id_to_del, user_id=1)
    
    assert success is True
    assert session.get(Categoria, id_to_del) is None
    
    # Verify Audit trail for DELETE
    audit = session.exec(select(AuditLog).where(AuditLog.accion == "DELETE")).first()
    assert audit is not None
    assert audit.id_entidad == id_to_del
