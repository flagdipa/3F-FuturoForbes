import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .config import settings
from .api.v1.router import api_router
from .api.ui_router import router as ui_router
from .api.auth.router import router as auth_router
from .core.database import init_db

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Starting 3F System...")
    # Initialize database tables
    init_db()
    # Initialize plugins, check DB migrations, etc.
    yield
    # Shutdown logic
    logger.info("Shutting down 3F System...")

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan
    )

    # Set all CORS enabled origins
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Mount Static Files
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    static_dir = os.path.join(base_dir, "frontend", "static")
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

    # API Routers
    app.include_router(auth_router, prefix="/api")
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    # Retrocompatibilidad - Alias en la raíz de API que envían al router v1
    app.include_router(api_router, prefix="/api")
    
    # Mapeos directos para rutas antiguas duras usando el nuevo enrutador
    from .api.v1.accounts import router as v1_accounts
    from .api.v1.transactions import router as v1_transactions
    from .api.retro import router as retro_router
    
    app.include_router(v1_accounts, prefix="/api/cuentas", tags=["retro-accounts"])
    app.include_router(v1_transactions, prefix="/api/transactions", tags=["retro-transactions"])
    app.include_router(v1_transactions, prefix="/api/transacciones", tags=["retro-transacciones"])
    app.include_router(retro_router, prefix="/api", tags=["retro-dummies"])

    app.include_router(ui_router)

    return app

app = create_app()
