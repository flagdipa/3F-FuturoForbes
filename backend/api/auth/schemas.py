from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class UsuarioCrear(BaseModel):
    email: EmailStr
    password: str
    nombre: Optional[str] = None
    apellido: Optional[str] = None

class UsuarioLectura(BaseModel):
    id_usuario: int
    email: EmailStr
    bloqueado: bool

    class Config:
        from_attributes = True

# --- Profile & Password ---

class ProfileRead(BaseModel):
    id_usuario: int
    email: EmailStr
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    theme_preference: str = "dark_neon"

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class RecuperarPasswordRequest(BaseModel):
    email: EmailStr
