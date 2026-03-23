from fastapi import APIRouter
from . import transactions, accounts, investments, ia, reports, budgets, goals, assets, categories, payees, institutions, vault, plugins, recurring, tags, themes, preferences
from .budgets.router import router as budgets_router
from .goals.router import router as goals_router

api_router = APIRouter()

# English Routes
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(investments.router, prefix="/investments", tags=["investments"])
api_router.include_router(ia.router, prefix="/ia", tags=["ai", "gemini"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(budgets_router, prefix="/budgets", tags=["budgets"])
api_router.include_router(goals_router, prefix="/goals", tags=["goals"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(payees.router, prefix="/payees", tags=["payees"])
api_router.include_router(assets.router, prefix="/assets", tags=["assets"])
api_router.include_router(institutions.router, prefix="/institutions", tags=["institutions"])
api_router.include_router(vault.router, prefix="/vault", tags=["vault"])
api_router.include_router(plugins.router, prefix="/plugins", tags=["plugins"])
api_router.include_router(recurring.router, prefix="/recurring", tags=["recurring"])
api_router.include_router(tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(themes.router, prefix="/themes", tags=["themes"])
api_router.include_router(preferences.router, prefix="/users/me", tags=["preferences"])

# Spanish Aliases for legacy/mixed frontend support
api_router.include_router(accounts.router, prefix="/cuentas", include_in_schema=False)
api_router.include_router(transactions.router, prefix="/transacciones", include_in_schema=False)
api_router.include_router(reports.router, prefix="/reportes", include_in_schema=False)
api_router.include_router(categories.router, prefix="/categorias", include_in_schema=False)
api_router.include_router(payees.router, prefix="/beneficiarios", include_in_schema=False)


@api_router.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}
