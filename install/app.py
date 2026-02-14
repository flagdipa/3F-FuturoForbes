"""
Aplicación FastAPI del Wizard de Instalación de FuturoForbes 3F
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os
import sys

# Agregar el directorio raíz del proyecto al path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importar módulos especializados
from install.requirements_checker import run_all_checks
from install.database_installer import (
    test_connection, create_database_if_not_exists,
    run_migrations, insert_initial_data, create_admin_user
)
from install.config_generator import (
    generate_secret_key, create_env_file,
    validate_config, backup_existing_env
)
from backend.core.install_checker import mark_as_installed, rename_install_folder

app = FastAPI(title="3F Installation Wizard")

# Configurar estáticos y templates
# Nota: Al montarse en /install, el path debe ser relativo al archivo
current_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

from backend.core.install_checker import is_installed

# --- Fail-safe: Si ya está instalado, el wizard no debe correr ---
@app.middleware("http")
async def check_installed_middleware(request: Request, call_next):
    # Permitir estáticos siempre para que las páginas de error se vean bien
    if request.url.path.startswith("/static"):
        return await call_next(request)
        
    # Si ya hay evidencia de instalación (.env y .installed), fuera de aquí redirección
    if is_installed():
        return RedirectResponse(url="/")
        
    return await call_next(request)

# --- Modelos Pydantic ---
class DatabaseConfig(BaseModel):
    db_type: str
    host: str
    port: int
    user: str
    password: str = ""
    database: str
    create_if_not_exists: bool = False

class AdminUserConfig(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    full_name: Optional[str] = None

class SystemConfig(BaseModel):
    system_name: str = "FuturoForbes 3F"
    default_currency: str = "ARS"
    language: str = "es"
    install_demo_data: bool = False

class InstallationRequest(BaseModel):
    db_config: DatabaseConfig
    admin_config: AdminUserConfig
    system_config: SystemConfig

# --- Rutas de Navegación ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return RedirectResponse(url="/install/step/1")

@app.get("/step/{step_number}", response_class=HTMLResponse)
async def wizard_step(request: Request, step_number: int):
    # Validar paso
    if step_number < 1 or step_number > 6:
        return RedirectResponse(url="/install/step/1")
    
    # Cada paso tiene su template
    template_name = f"step{step_number}_"
    if step_number == 1: template_name += "welcome.html"
    elif step_number == 2: template_name += "requirements.html"
    elif step_number == 3: template_name += "database.html"
    elif step_number == 4: template_name += "admin.html"
    elif step_number == 5: template_name += "config.html"
    elif step_number == 6: template_name += "complete.html"
    
    return templates.TemplateResponse(template_name, {
        "request": request,
        "step": step_number,
        "total_steps": 6
    })

# --- API Endpoints ---
@app.post("/api/check-requirements")
async def api_check_requirements():
    return run_all_checks()

@app.post("/api/test-database")
async def api_test_database(config: DatabaseConfig):
    return test_connection(
        config.db_type, config.host, config.port, 
        config.user, config.password, config.database
    )

@app.post("/api/validate-admin")
async def api_validate_admin(config: AdminUserConfig):
    if config.password != config.confirm_password:
        return {"success": False, "message": "Passwords do not match"}
    if len(config.password) < 8:
        return {"success": False, "message": "Password too short"}
    return {"success": True}

@app.post("/api/verify-system")
async def api_verify_system():
    """
    Verifica que el sistema esté operativo tras la instalación (PrestaShop verify step).
    Si todo está OK, intenta renombrar la carpeta install.
    """
    from backend.core.database import engine
    from sqlalchemy import text
    
    try:
        # Usar el engine global configurado con el nuevo .env
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Si llegamos aquí, el sistema funciona. Intentar renombrar carpeta
        rename_res = rename_install_folder()
        
        return {
            "success": True, 
            "message": "System is functional. Security cleanup completed.",
            "cleanup": rename_res
        }
    except Exception as e:
        import traceback
        return {
            "success": False, 
            "message": f"System verification failed: {str(e)}",
            "traceback": traceback.format_exc()
        }

@app.post("/api/install")
async def api_run_install(req: InstallationRequest):
    log = []
    try:
        # 1. Backup y .env
        backup_path = backup_existing_env()
        if backup_path: log.append({"step": "backup_env", "status": "success", "msg": f"Backup: {backup_path}"})
        
        # Generar config
        conn_url = f"{req.db_config.db_type}+pymysql://{req.db_config.user}:{req.db_config.password}@{req.db_config.host}:{req.db_config.port}/{req.db_config.database}"
        secret_key = generate_secret_key()
        
        env_result = create_env_file({
            "DATABASE_URL": conn_url,
            "SECRET_KEY": secret_key,
            "SKIP_INSTALL_FOLDER_CHECK": "true"
        })
        log.append({"step": "create_env", "status": "success" if env_result.get("success") else "failed"})
        
        # 2. Database
        if req.db_config.create_if_not_exists:
            db_res = create_database_if_not_exists(
                req.db_config.db_type, req.db_config.host, req.db_config.port,
                req.db_config.user, req.db_config.password, req.db_config.database
            )
            log.append({"step": "create_database", "status": "success" if db_res.get("success") else "failed"})
        
        # 3. Migrations
        mig_res = run_migrations(conn_url)
        log.append({"step": "run_migrations", "status": "success" if mig_res.get("success") else "failed"})
        
        # 4. Initial Data
        data_res = insert_initial_data(conn_url)
        log.append({"step": "insert_initial_data", "status": "success" if data_res.get("success") else "failed"})
        
        # 5. Admin
        adm_res = create_admin_user(
            conn_url, req.admin_config.username, req.admin_config.email, 
            req.admin_config.password, req.admin_config.full_name
        )
        log.append({"step": "create_admin", "status": "success" if adm_res.get("success") else "failed"})
        
        # 6. Finalizar
        mark_as_installed()
        log.append({"step": "mark_installed", "status": "success"})
        
        return {
            "success": True, 
            "log": log,
            "admin_username": req.admin_config.username,
            "admin_email": req.admin_config.email
        }
    except Exception as e:
        return {"success": False, "message": str(e), "log": log}
