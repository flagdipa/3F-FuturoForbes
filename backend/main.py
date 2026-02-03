from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .core.config import settings
from .core.config_inf import config_inf
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
from .api.custom_fields.router import router as custom_fields_router
import os

app = FastAPI(
    title=config_inf.get("SISTEMA", "nombre", "Fer Futuro Forbes (3F)"),
    description="Sistema de Finanzas Personales con IA y Estética Neón Futurista",
    version=config_inf.get("SISTEMA", "version", "1.0.0")
)

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
app.include_router(custom_fields_router, prefix="/api")

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

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

@app.get("/api/estado")
async def api_status():
    return {"mensaje": "Bienvenido a la API de Fer Futuro Forbes (3F)", "estado": "en línea"}
