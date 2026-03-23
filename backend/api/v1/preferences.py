"""
User UI Preferences API
Handles sidebar order and other user-specific UI settings.
Uses SystemConfig table with user-scoped keys.
"""
import json
from typing import Optional
from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from pydantic import BaseModel
from ...dependencies import get_db
from ...models import SystemConfig

router = APIRouter()


class UIPreferencesPayload(BaseModel):
    sidebar_order: Optional[list] = None


# Default sidebar order — used when no user preference exists
DEFAULT_SIDEBAR_ORDER = [
    "dashboard",
    "scheduled",
    "transactions_ars",
    "transactions_usd",
    "accounts_favoritas",
    "accounts_bancarias",
    "accounts_tarjeta",
    "accounts_billeteras",
    "accounts_efectivo",
    "accounts_plazo",
    "budgets",
    "goals",
    "modules",
    "reports",
    "vault",
    "settings",
]


def _config_key() -> str:
    return "sidebar_order"


@router.get("/ui-preferences")
def get_ui_preferences(
    db: Session = Depends(get_db),
):
    key = _config_key()
    row = db.exec(select(SystemConfig).where(SystemConfig.key == key)).first()
    if row:
        try:
            order = json.loads(row.value)
        except Exception:
            order = DEFAULT_SIDEBAR_ORDER
    else:
        order = DEFAULT_SIDEBAR_ORDER
    return {"sidebar_order": order}


@router.put("/ui-preferences")
def update_ui_preferences(
    payload: UIPreferencesPayload,
    db: Session = Depends(get_db),
):
    key = _config_key()
    row = db.exec(select(SystemConfig).where(SystemConfig.key == key)).first()

    value = json.dumps(payload.sidebar_order or DEFAULT_SIDEBAR_ORDER)

    if row:
        row.value = value
    else:
        row = SystemConfig(
            key=key,
            value=value,
            description="User sidebar item order preference",
        )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"status": "ok", "sidebar_order": json.loads(row.value)}

