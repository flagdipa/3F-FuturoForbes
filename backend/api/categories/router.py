from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from ...core.database import get_session
from ...models.models import Categoria, Usuario
from .schemas import CategoriaCrear, CategoriaLectura, CategoriaArbol
from ..base_crud import BaseCRUDService
from ..schemas.common import PaginatedResponse
from ..auth.deps import get_current_user
from typing import List

router = APIRouter(prefix="/categorias", tags=["Categorías"])

# Initialize generic service
category_service = BaseCRUDService[Categoria, CategoriaCrear, CategoriaCrear](Categoria)

@router.get("/", response_model=PaginatedResponse[CategoriaLectura])
def listar_categorias(
    offset: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """List all categories with pagination"""
    return category_service.list(session, offset, limit)

@router.get("/arbol", response_model=List[CategoriaArbol])
def obtener_arbol_categorias(session: Session = Depends(get_session)):
    """Retrieve categories structured as a tree (special view)"""
    all_categories = session.exec(select(Categoria)).all()
    
    # Construir mapa de categorías
    category_map = {cat.id_categoria: CategoriaArbol.from_orm(cat) for cat in all_categories}
    tree = []
    
    for cat_id, cat_tree in category_map.items():
        if cat_tree.id_padre is None:
            tree.append(cat_tree)
        else:
            parent = category_map.get(cat_tree.id_padre)
            if parent:
                parent.subcategorias.append(cat_tree)
    
    return tree

@router.post("/", response_model=CategoriaLectura)
def crear_categoria(
    categoria_in: CategoriaCrear, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Create a new category with audit"""
    return category_service.create(
        session, 
        categoria_in,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )

@router.get("/{categoria_id}", response_model=CategoriaLectura)
def obtener_categoria(categoria_id: int, session: Session = Depends(get_session)):
    """Get a category by ID"""
    cat = category_service.get(session, categoria_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return cat

@router.put("/{categoria_id}", response_model=CategoriaLectura)
def actualizar_categoria(
    categoria_id: int,
    categoria_in: CategoriaCrear, # Using CategoriaCrear for now or CategoriaUpdate
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Update a category with audit"""
    db_obj = category_service.get(session, categoria_id)
    if not db_obj:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    return category_service.update(
        session,
        db_obj=db_obj,
        obj_in=categoria_in,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )

@router.delete("/{categoria_id}")
def eliminar_categoria(
    categoria_id: int, 
    request: Request,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Delete a category with audit"""
    success = category_service.delete(
        session, 
        categoria_id,
        user_id=current_user.id_usuario,
        ip_address=request.client.host
    )
    if not success:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"message": "Categoría eliminada correctamente"}
