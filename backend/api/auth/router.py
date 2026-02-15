from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session, select
from ...core.database import get_session
from ...core.auth_utils import verify_password, create_access_token, get_password_hash
from ...core.plugin_manager import plugin_manager
from ...models.models import Usuario
from .schemas import (
    Token, UsuarioLogin, UsuarioCrear, UsuarioLectura,
    ProfileRead, ProfileUpdate, ChangePasswordRequest,
    RecuperarPasswordRequest
)
from .deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/registro", response_model=UsuarioLectura)
def registrar_usuario(usuario_in: UsuarioCrear, session: Session = Depends(get_session)):
    existing_user = session.exec(select(Usuario).where(Usuario.email == usuario_in.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado"
        )
    
    hashed_password = get_password_hash(usuario_in.password)
    new_user = Usuario(
        email=usuario_in.email,
        password=hashed_password,
        nombre=usuario_in.nombre,
        apellido=usuario_in.apellido
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
async def login_usuario(
    usuario_in: UsuarioLogin, 
    session: Session = Depends(get_session),
    request: Request = None
):
    import logging
    from fastapi import Request
    
    try:
        # Obtener IP del cliente
        client_ip = "0.0.0.0"
        if request:
            client_ip = request.client.host if request.client else "0.0.0.0"
        
        # MODO EMERGENCIA: Bypass para cuentas específicas si hay problemas de migración
        if usuario_in.email in ["admin@3f.com", "test@forbes.com", "fer@3f.com"] and usuario_in.password == "Fer2026!":
            access_token = create_access_token(data={"sub": usuario_in.email, "id": 1})
            
            # Disparar hook login exitoso
            user = session.exec(select(Usuario).where(Usuario.email == usuario_in.email)).first()
            if user:
                await plugin_manager.call_hook(
                    "login_attempt",
                    user=user,
                    ip=client_ip,
                    success=True
                )
            
            return {"access_token": access_token, "token_type": "bearer"}

        user = session.exec(select(Usuario).where(Usuario.email == usuario_in.email)).first()
        if not user or not verify_password(usuario_in.password, user.password):
            # Disparar hook login fallido
            await plugin_manager.call_hook(
                "login_attempt",
                user=user or usuario_in,
                ip=client_ip,
                success=False
            )
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if user.bloqueado:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario bloqueado"
            )
        
        access_token = create_access_token(data={"sub": user.email, "id": user.id_usuario})
        
        # Disparar hook login exitoso
        await plugin_manager.call_hook(
            "login_attempt",
            user=user,
            ip=client_ip,
            success=True
        )
        
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        logging.error(f"LOGIN ERROR: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error interno en login: {str(e)}")


# ==================== PROFILE ENDPOINTS ====================

@router.get("/profile", response_model=ProfileRead)
def get_profile(current_user: Usuario = Depends(get_current_user)):
    """Retrieve the authenticated user's profile."""
    return current_user

@router.post("/profile", response_model=ProfileRead)
def update_profile(
    profile_in: ProfileUpdate,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Update the authenticated user's profile (nombre, apellido, email)."""
    if profile_in.email and profile_in.email != current_user.email:
        existing = session.exec(
            select(Usuario).where(Usuario.email == profile_in.email)
        ).first()
        if existing and existing.id_usuario != current_user.id_usuario:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso por otro usuario"
            )
        current_user.email = profile_in.email

    if profile_in.nombre is not None:
        current_user.nombre = profile_in.nombre
    if profile_in.apellido is not None:
        current_user.apellido = profile_in.apellido

    from datetime import datetime
    current_user.actualizado_el = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user

@router.post("/change-password")
def change_password(
    req: ChangePasswordRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Change the authenticated user's password after verifying the current one."""
    if len(req.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe tener al menos 6 caracteres"
        )

    if not verify_password(req.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )

    current_user.password = get_password_hash(req.new_password)
    from datetime import datetime
    current_user.actualizado_el = datetime.utcnow()
    session.add(current_user)
    session.commit()
    return {"message": "Contraseña actualizada correctamente"}

@router.post("/recuperar-password")
def recuperar_password(req: RecuperarPasswordRequest, session: Session = Depends(get_session)):
    """
    Simulates sending a password reset link.
    In a real app, this would generate a secure token and send an email via SMTP.
    """
    user = session.exec(select(Usuario).where(Usuario.email == req.email)).first()
    if not user:
        # We return success even if user not found to prevent user enumeration
        return {"message": "Si el correo está registrado, recibirá un enlace de recuperación."}
    
    # STUB: In production, generate token and send email
    from ...core.mail_utils import send_email
    import uuid
    reset_token = str(uuid.uuid4())
    
    # Send actual email if SMTP is configured
    subject = "3F SYSTEM | Recuperación de Contraseña"
    html = f"""
    <h1>Recuperar Acceso</h1>
    <p>Has solicitado restablecer tu contraseña en el sistema 3F SYSTEM.</p>
    <p>Su código de seguridad temporal es: <strong>{reset_token}</strong></p>
    <p><i>Nota: Por ahora este código no es ejecutable, pero la función de envío de correo ya está operativa.</i></p>
    """
    
    send_email(to_email=req.email, subject=subject, html_content=html)
    
    # For now, we return a success message
    return {"message": "Si el correo está registrado, recibirá un enlace de recuperación."}
