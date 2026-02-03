from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...core.database import get_session
from ...models.models import Categoria
from .schemas import CategoriaCrear, CategoriaLectura, CategoriaArbol
from typing import List

router = APIRouter(prefix="/categorias", tags=["Categorías"]) # Renombrado

@router.get("/", response_model=List[CategoriaLectura])
def listar_categorias(session: Session = Depends(get_session)):
    return session.exec(select(Categoria)).all()

@router.get("/arbol", response_model=List[CategoriaArbol])
def obtener_arbol_categorias(session: Session = Depends(get_session)):
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
def crear_categoria(categoria_in: CategoriaCrear, session: Session = Depends(get_session)):
    nueva_categoria = Categoria.from_orm(categoria_in)
    session.add(nueva_categoria)
    session.commit()
    session.refresh(nueva_categoria)
    return nueva_categoria
