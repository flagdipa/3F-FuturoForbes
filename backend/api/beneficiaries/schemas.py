from pydantic import BaseModel
from typing import Optional

class BeneficiarioBase(BaseModel):
    nombre_beneficiario: str
    id_categoria: Optional[int] = None
    cbu: Optional[str] = None
    numero: Optional[str] = None
    sitio_web: Optional[str] = None
    notas: Optional[str] = None
    activo: int = 1
    patron_busqueda: Optional[str] = None
    cuit: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[str] = None
    oculto: int = 0
    banco: Optional[str] = None

class BeneficiarioCrear(BeneficiarioBase): # Renombrado
    pass

class BeneficiarioLectura(BeneficiarioBase): # Renombrado
    id_beneficiario: int

    class Config:
        from_attributes = True
