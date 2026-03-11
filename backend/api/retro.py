from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from ..dependencies import get_db
from sqlmodel import Session, select
from ..models import Category, Tag, Payee, Transaction, TransactionSplit, Account
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
import asyncio
import json

class RetroBeneficiarioIn(BaseModel):
    nombre_beneficiario: str
    sitio_web: str | None = None
    notas: str | None = None
    cbu: str | None = None
    cuit: str | None = None
    telefono: str | None = None
    direccion: str | None = None
    banco: str | None = None
    activo: int = 1


router = APIRouter()

@router.get("/themes/current")
def get_theme():
    return {"status": "ok", "theme": "default"}

@router.get("/stocks/")
def get_stocks():
    return []

@router.get("/assets/")
def get_assets():
    return []

@router.get("/plugins/activos")
def get_plugins():
    return []

@router.get("/plugins/argentina-datos/dolar")
def get_dolar_mock():
    # Retorna null para disparar silenciosamente el fallback del frontend en vez de dar un error 404
    return None

@router.get("/forecasting/insights")
def get_insights_mock():
    # Retorna null para disparar silenciosamente el fallback del frontend
    return None

@router.get("/categorias/")
def get_categories(db: Session = Depends(get_db)):
    # The frontend expects array of categories with specific Spanish fields
    cats = db.exec(select(Category)).all()
    res = []
    for c in cats:
        res.append({
            "id_categoria": c.id,
            "nombre_categoria": c.name,
            "tipo_categoria": c.type,
            "color": c.color or "#FFFFFF",
            "full_name": c.name # used by the frontend
        })
    return res

@router.get("/cuentas/")
def get_cuentas(db: Session = Depends(get_db)):
    """Retro-compat: Returns accounts in V1 Spanish format."""
    accounts = db.exec(select(Account).where(Account.deleted_at == None)).all()
    res = []
    for a in accounts:
        res.append({
            "id_cuenta": a.id,
            "nombre_cuenta": a.name,
            "tipo_cuenta": a.type.value if hasattr(a.type, 'value') else str(a.type),
            "moneda": a.currency_code,
            "saldo_actual": float(a.current_balance),
            "activo": 1 if a.is_active else 0
        })
    return res

@router.get("/beneficiarios/")
def get_payees(db: Session = Depends(get_db)):
    payees = db.exec(select(Payee)).all()
    res = []
    for p in payees:
        extra = {}
        if p.notes and p.notes.startswith('{'):
            try:
                extra = json.loads(p.notes)
            except:
                extra = {"notas": p.notes}
        else:
            extra = {"notas": p.notes}

        res.append({
            "id_beneficiario": p.id,
            "nombre_beneficiario": p.name,
            "sitio_web": p.website or "",
            "notas": extra.get("notas", ""),
            "cbu": extra.get("cbu", ""),
            "cuit": extra.get("cuit", ""),
            "telefono": extra.get("telefono", ""),
            "direccion": p.address or "",
            "banco": extra.get("banco", ""),
            "activo": 1,
            "oculto": 0
        })
    return res

@router.post("/beneficiarios/")
def create_payee(data: RetroBeneficiarioIn, db: Session = Depends(get_db)):
    notes_dict = {
        "notas": data.notas or "",
        "cbu": data.cbu or "",
        "cuit": data.cuit or "",
        "telefono": data.telefono or "",
        "banco": data.banco or ""
    }
    
    payee = Payee(
        user_id=1,  # fallback as we aren't enforcing auth here directly for retro compatibility, though ideally we use getattr_current_user
        name=data.nombre_beneficiario,
        address=data.direccion,
        website=data.sitio_web,
        notes=json.dumps(notes_dict, ensure_ascii=False)
    )
    db.add(payee)
    db.commit()
    db.refresh(payee)
    return {"status": "ok", "id": payee.id}

@router.put("/beneficiarios/{payee_id}")
def update_payee(payee_id: int, data: RetroBeneficiarioIn, db: Session = Depends(get_db)):
    payee = db.get(Payee, payee_id)
    if not payee:
        raise HTTPException(status_code=404, detail="Beneficiario no encontrado")
        
    notes_dict = {
        "notas": data.notas or "",
        "cbu": data.cbu or "",
        "cuit": data.cuit or "",
        "telefono": data.telefono or "",
        "banco": data.banco or ""
    }
    
    payee.name = data.nombre_beneficiario
    payee.address = data.direccion
    payee.website = data.sitio_web
    payee.notes = json.dumps(notes_dict, ensure_ascii=False)
    db.add(payee)
    db.commit()
    return {"status": "ok"}

@router.delete("/beneficiarios/{payee_id}")
def delete_payee(payee_id: int, db: Session = Depends(get_db)):
    payee = db.get(Payee, payee_id)
    if not payee:
        raise HTTPException(status_code=404, detail="Beneficiario no encontrado")
    
    # check for txs
    txs = db.exec(select(Transaction).where(Transaction.payee_id == payee_id)).first()
    if txs:
        raise HTTPException(status_code=400, detail="Cannot delete payee with transactions")
        
    db.delete(payee)
    db.commit()
    return {"status": "ok"}

@router.get("/tags/")
def get_tags(db: Session = Depends(get_db)):
    tags = db.exec(select(Tag)).all()
    res = []
    for t in tags:
        res.append({
            "id_etiqueta": t.id,
            "nombre_etiqueta": t.name,
            "color": t.color
        })
    return res

# Simulate an empty but held open connection to satisfy EventSource silently
async def keep_alive_stream():
    yield "event: ping\ndata: {}\n\n"
    while True:
        await asyncio.sleep(60)
        yield "event: ping\ndata: {}\n\n"

@router.get("/notifications/stream")
def notifications_stream():
    return StreamingResponse(keep_alive_stream(), media_type="text/event-stream")
