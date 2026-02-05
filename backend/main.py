from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .core.config import settings
from .core.config_inf import config_inf
from .core.logging_config import setup_logging
from .core.security_middleware import limiter, SecurityHeadersMiddleware, _rate_limit_exceeded_handler
from .core.exceptions import APIException
from slowapi.errors import RateLimitExceeded
from .api.auth.router import router as auth_router
from .api.accounts.router_divisa import router as currency_router
from .api.accounts.router import router as account_router
from .api.categories.router import router as category_router
from .api.beneficiaries.router import router as beneficiary_router
from .api.transactions.router import router as transaction_router
from .api.transactions.router_resumen import router as summary_router
from .api.ia.router import router as ia_router
from .api.budgets.router import router as budget_router
from .api.reports.router import router as report_router
# Phase 1 MMEX Features
from .api.tags.router import router as tags_router
from .api.attachments.router import router as attachments_router
from .api.currency_history.router import router as currency_history_router
from .api.recurring.router import router as recurring_router
from .api.assets.router import router as assets_router
from .api.stocks.router import router as stocks_router
from .api.budgets.router_setup import router as budget_setup_router
from .api.config.router import router as config_router
from .api.config.router_plugins import router as plugins_router
from .api.custom_fields.router import router as custom_fields_router
from .api.layouts.router import router as layouts_router
from .api.themes.router import router as themes_router
from .api.notifications.router import router as notifications_router
from .api.reports.router_exports import router as exports_router
from .api.wealth.router import router as wealth_router
from .api.fx.router import router as fx_router
from .api.vault.router import router as vault_router
from .api.audit.router import router as audit_router
from .api.health.router import router as health_router
from .api.reconciliation.router import router as reconciliation_router
from .models import * # Asegura registro de tablas de SQLModel
from .core.scheduler import start_scheduler
from datetime import datetime
import os

# Setup logging
setup_logging(environment="development")

app = FastAPI(
    title=config_inf.get("SISTEMA", "nombre", "Fer Futuro Forbes (3F)"),
    description="""## FuturoForbes (3F) - Sistema de Finanzas Personales
    
    ### Características
    - IA integrada para análisis financiero
    - Gestión multidivisa con tasas en tiempo real
    - Sistema de auditoría completo
    - Presupuestos inteligentes
    - Reportes avanzados
    
    ### Autenticación
    Use JWT Bearer tokens. Obtenga el token desde `/api/auth/login`
    
    ### Rate Limiting
    100 requests por minuto por dirección IP
    """,
    version=config_inf.get("SISTEMA", "version", "1.0.0"),
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Rate limiter state
app.state.limiter = limiter

@app.on_event("startup")
def on_startup():
    start_scheduler()
    import logging
    logging.info("🚀 FuturoForbes (3F) starting up...")
    logging.info(f"📋 Version: {config_inf.get('SISTEMA', 'version', '1.0.0')}")

# Exception handlers
@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    """Handle custom API exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded"""
    return JSONResponse(
        status_code=429,
        content={
            "error_code": "RATE_LIMIT_EXCEEDED",
            "message": "Too many requests, please try again later",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servir archivos estáticos
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Configurar Templates
templates = Jinja2Templates(directory="frontend/templates")

# Incluir Routers de API (Prefijo /api)
app.include_router(auth_router, prefix="/api")
app.include_router(currency_router, prefix="/api")
app.include_router(account_router, prefix="/api")
app.include_router(category_router, prefix="/api")
app.include_router(beneficiary_router, prefix="/api")
app.include_router(transaction_router, prefix="/api")
app.include_router(summary_router, prefix="/api")
app.include_router(ia_router, prefix="/api")
app.include_router(budget_router, prefix="/api")
app.include_router(report_router, prefix="/api")
# Phase 1 MMEX Features
app.include_router(tags_router, prefix="/api")
app.include_router(attachments_router, prefix="/api")
app.include_router(currency_history_router, prefix="/api")
app.include_router(recurring_router, prefix="/api")
app.include_router(assets_router, prefix="/api")
app.include_router(stocks_router, prefix="/api")
app.include_router(budget_setup_router, prefix="/api/budgets")
app.include_router(config_router, prefix="/api")
app.include_router(plugins_router, prefix="/api")
app.include_router(custom_fields_router, prefix="/api")
app.include_router(layouts_router, prefix="/api")
app.include_router(themes_router, prefix="/api")
app.include_router(notifications_router, prefix="/api")
app.include_router(exports_router, prefix="/api")
app.include_router(wealth_router, prefix="/api")
app.include_router(fx_router, prefix="/api")
app.include_router(vault_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(reconciliation_router, prefix="/api")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/plugins")
async def plugins_page(request: Request):
    return templates.TemplateResponse("plugins.html", {"request": request})

@app.get("/cuentas")
async def accounts_page(request: Request):
    return templates.TemplateResponse("accounts.html", {"request": request})

@app.get("/transacciones")
async def transactions_page(request: Request):
    return templates.TemplateResponse("transactions.html", {"request": request})

@app.get("/categorias")
async def categories_page(request: Request):
    return templates.TemplateResponse("categories.html", {"request": request})

@app.get("/presupuestos")
async def budgets_page(request: Request):
    return templates.TemplateResponse("budgets.html", {"request": request})

@app.get("/reportes")
async def reports_page(request: Request):
    return templates.TemplateResponse("reports.html", {"request": request})

@app.get("/beneficiarios") # Nueva ruta para beneficiarios
async def beneficiaries_page(request: Request):
    return templates.TemplateResponse("beneficiaries.html", {"request": request})

@app.get("/etiquetas") # Nueva ruta para etiquetas
async def tags_page(request: Request):
    return templates.TemplateResponse("tags.html", {"request": request})

@app.get("/programadas") # Nueva ruta para transacciones programadas
async def recurring_page(request: Request):
    return templates.TemplateResponse("recurring.html", {"request": request})

@app.get("/activos") # Nueva ruta para activos
async def assets_page(request: Request):
    return templates.TemplateResponse("assets.html", {"request": request})

@app.get("/inversiones") # Nueva ruta para inversiones
async def stocks_page(request: Request):
    return templates.TemplateResponse("stocks.html", {"request": request})

@app.get("/settings")
async def settings_page(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})

@app.get("/vault", response_class=HTMLResponse)
async def vault_page(request: Request):
    return templates.TemplateResponse("vault.html", {"request": request})

@app.get("/audit", response_class=HTMLResponse)
async def audit_page(request: Request):
    return templates.TemplateResponse("audit.html", {"request": request})

@app.get("/import", response_class=HTMLResponse)
async def import_page(request: Request):
    return templates.TemplateResponse("import_csv.html", {"request": request})

@app.get("/api/estado")
async def api_status():
    return {"mensaje": "Bienvenido a la API de Fer Futuro Forbes (3F)", "estado": "en línea"}
