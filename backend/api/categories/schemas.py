from pydantic import BaseModel
from typing import Optional, List

class CategoriaBase(BaseModel):
    nombre_categoria: str
    activo: int = 1
    id_padre: Optional[int] = None
    color: Optional[str] = None
    notas: Optional[str] = None

class CategoriaCrear(CategoriaBase): 
    pass

class CategoriaUpdate(BaseModel):
    nombre_categoria: Optional[str] = None
    activo: Optional[int] = None
    id_padre: Optional[int] = None
    color: Optional[str] = None
    notas: Optional[str] = None

class CategoriaLectura(CategoriaBase): 
    id_categoria: int

    class Config:
        from_attributes = True

class CategoriaArbol(CategoriaLectura): # Renombrado (Tree -> Arbol)
    subcategorias: List["CategoriaArbol"] = []

CategoriaArbol.update_forward_refs()

class CategoriaCombinar(BaseModel):
    id_origen: int
    id_destino: int
    eliminar_origen: bool = False

class CategoriaStats(BaseModel):
    transacciones: int
    divisiones: int
    programadas: int
    divisiones_programadas: int
    beneficiarios: int
    presupuestos: int
