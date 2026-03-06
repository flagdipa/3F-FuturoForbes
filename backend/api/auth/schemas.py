from pydantic import BaseModel, EmailStr
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserRead(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    is_admin: bool
    theme_id: str
    language: str

    class Config:
        from_attributes = True

# --- Profile & Password ---

class ProfileRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str] = None
    theme_id: str
    language: str

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    theme_id: Optional[str] = None
    language: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class RecoverPasswordRequest(BaseModel):
    email: EmailStr
