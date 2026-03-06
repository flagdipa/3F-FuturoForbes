from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

router = APIRouter()

# Setup templates directory
# File is at: backend/api/ui_router.py -> 3 levels up to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATES_DIR = os.path.join(BASE_DIR, "frontend", "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@router.get("/", response_class=HTMLResponse)
async def dashboard_view(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/accounts", response_class=HTMLResponse)
async def accounts_view(request: Request):
    return templates.TemplateResponse("accounts/index.html", {"request": request})

@router.get("/transacciones", response_class=HTMLResponse)
async def transactions_view(request: Request):
    return templates.TemplateResponse("transactions.html", {"request": request})

@router.get("/transactions", response_class=HTMLResponse)
async def transactions_en_view(request: Request):
    return templates.TemplateResponse("transactions.html", {"request": request})

@router.get("/accounts/{account_id}/reconcile", response_class=HTMLResponse)
async def reconcile_view(request: Request, account_id: int):
    return templates.TemplateResponse("accounts/reconcile.html", {"request": request, "account_id": account_id})

@router.get("/investments", response_class=HTMLResponse)
async def investments_view(request: Request):
    return templates.TemplateResponse("investments/index.html", {"request": request})

@router.get("/reports", response_class=HTMLResponse)
async def reports_view(request: Request):
    return templates.TemplateResponse("reports/index.html", {"request": request})

@router.get("/budgets", response_class=HTMLResponse)
async def budgets_view(request: Request):
    return templates.TemplateResponse("budgets/index.html", {"request": request})

@router.get("/metas", response_class=HTMLResponse)
async def metas_view(request: Request):
    return templates.TemplateResponse("goals/index.html", {"request": request})

@router.get("/login", response_class=HTMLResponse)
async def login_view(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_view(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/forgot-password", response_class=HTMLResponse)
async def forgot_password_view(request: Request):
    return templates.TemplateResponse("forgot-password.html", {"request": request})

@router.get("/plugins", response_class=HTMLResponse)
async def plugins_view(request: Request):
    return templates.TemplateResponse("plugins.html", {"request": request})

@router.get("/entidades", response_class=HTMLResponse)
async def entidades_view(request: Request):
    return templates.TemplateResponse("financial_entities.html", {"request": request})

@router.get("/programadas", response_class=HTMLResponse)
async def programadas_view(request: Request):
    return templates.TemplateResponse("recurring.html", {"request": request})

@router.get("/settings", response_class=HTMLResponse)
async def settings_view(request: Request):
    return templates.TemplateResponse("settings.html", {"request": request})


