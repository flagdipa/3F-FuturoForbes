from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UsuarioLogin(BaseModel): # Renombrado a español
    email: EmailStr
    password: str

class UsuarioCrear(BaseModel): # Renombrado a español
    email: EmailStr
    password: str

class UsuarioLectura(BaseModel): # Renombrado a español
    id_usuario: int
    email: EmailStr
    bloqueado: bool

    class Config:
        from_attributes = True
