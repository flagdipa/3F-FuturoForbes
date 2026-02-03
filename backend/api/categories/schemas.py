from pydantic import BaseModel
from typing import Optional, List

class CategoriaBase(BaseModel):
    nombre_categoria: str
    activo: int = 1
    id_padre: Optional[int] = None
    color: Optional[str] = None
    notas: Optional[str] = None

class CategoriaCrear(CategoriaBase): # Renombrado
    pass

class CategoriaLectura(CategoriaBase): # Renombrado
    id_categoria: int

    class Config:
        from_attributes = True

class CategoriaArbol(CategoriaLectura): # Renombrado (Tree -> Arbol)
    subcategorias: List["CategoriaArbol"] = []

CategoriaArbol.update_forward_refs()
