from fastapi import APIRouter
from . import transactions, accounts, investments, ia, reports
from .budgets import router as budgets_router
from .goals import router as goals_router

api_router = APIRouter()

api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(investments.router, prefix="/investments", tags=["investments"])
api_router.include_router(ia.router, prefix="/ia", tags=["ai", "gemini"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(budgets_router.router, prefix="/budgets", tags=["budgets"])
api_router.include_router(goals_router.router, prefix="/goals", tags=["goals"])


@api_router.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0.0"}
