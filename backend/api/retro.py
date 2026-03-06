from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from ..dependencies import get_db
from sqlmodel import Session, select
from ..models import Category, Tag, Payee, Transaction, TransactionSplit, Account
from sqlalchemy.orm import selectinload
import asyncio

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

@router.get("/transacciones")
@router.get("/transacciones/")
def get_retro_transactions(db: Session = Depends(get_db)):
    txs = db.exec(select(Transaction).options(selectinload(Transaction.splits)).order_by(Transaction.date.desc())).all()
    res = []
    for t in txs:
        # Get primary split to guess account/category (first element)
        primary_split = t.splits[0] if t.splits else None
        
        monto = float(primary_split.amount) if primary_split else 0.0
        
        # Determine transaction type visually
        tipo = "ingreso" if monto > 0 else "gasto"
        
        res.append({
            "id_transaccion": t.id,
            "tipo_transaccion": tipo,
            "fecha_transaccion": t.date.isoformat(),
            "id_cuenta": primary_split.account_id if primary_split else None,
            "monto_transaccion": abs(monto),
            "codigo_transaccion": "deposit" if monto > 0 else "withdrawal",
            "descripcion": t.description,
            "id_beneficiario": t.payee_id,
            "id_categoria": primary_split.category_id if primary_split else None,
            "etiquetas": [],
            "estado": t.status,
            "saldo_resultante": 0.0
        })
    return {"data": res, "total": len(res)}


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

@router.get("/beneficiarios/")
def get_payees(db: Session = Depends(get_db)):
    payees = db.exec(select(Payee)).all()
    res = []
    for p in payees:
        res.append({
            "id_beneficiario": p.id,
            "nombre_beneficiario": p.name
        })
    return res

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
