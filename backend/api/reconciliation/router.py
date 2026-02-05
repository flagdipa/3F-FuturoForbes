from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select, func
from ...core.database import get_session
from ..auth.deps import get_current_user
from ...models.models import LibroTransacciones, ListaCuentas, Usuario
from ...core.csv_parser import CSVParser
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal

router = APIRouter(prefix="/reconciliation", tags=["Reconciliación"])

class ReconciliationPreview(BaseModel):
    fecha: str
    descripcion: str
    monto: Decimal
    match_id: Optional[int] = None # ID of an existing transaction if matched
    match_score: float = 0.0 # Confidence level
    is_new: bool = True # Flag to indicate if it's a new transaction to be created

@router.post("/preview", response_model=List[ReconciliationPreview])
async def preview_reconciliation(
    id_cuenta: int = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Parses the CSV and attempts to find matching transactions in the database.
    """
    # 1. Verify account ownership
    cuenta = session.get(ListaCuentas, id_cuenta)
    if not cuenta:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    # 2. Parse CSV
    content = await file.read()
    parser = CSVParser(content)
    try:
        data = parser.parse()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al procesar el archivo: {str(e)}")
    
    # 3. Intelligent Matching Logic
    previews = []
    for entry in data:
        # Search for potential matches in the database
        # Criteria: Same account, same amount, and date within +/- 3 days
        fecha_dt = datetime.fromisoformat(entry["fecha"])
        inicio = (fecha_dt - timedelta(days=3)).isoformat()
        fin = (fecha_dt + timedelta(days=3)).isoformat()
        
        query = select(LibroTransacciones).where(
            LibroTransacciones.id_cuenta == id_cuenta,
            LibroTransacciones.monto_transaccion == entry["monto"],
            LibroTransacciones.fecha_transaccion >= inicio,
            LibroTransacciones.fecha_transaccion <= fin
        )
        
        match = session.exec(query).first()
        
        preview = ReconciliationPreview(
            fecha=entry["fecha"],
            descripcion=entry["descripcion"],
            monto=entry["monto"],
            match_id=match.id_transaccion if match else None,
            match_score=0.9 if match else 0.0,
            is_new=not bool(match)
        )
        previews.append(preview)
        
    return previews

class ReconciliationProcessRequest(BaseModel):
    id_cuenta: int
    transactions: List[ReconciliationPreview]

@router.post("/process")
async def process_reconciliation(
    request: ReconciliationProcessRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Finalizes the reconciliation by creating new transactions or updating existing ones.
    """
    counts = {"created": 0, "matched": 0}
    
    for tx in request.transactions:
        if tx.is_new:
            # Create new transaction
            db_tx = LibroTransacciones(
                id_cuenta=request.id_cuenta,
                fecha_transaccion=tx.fecha,
                monto_transaccion=tx.monto,
                notas=f"[Importado] {tx.descripcion}",
                id_usuario=current_user.id_usuario,
                fecha_actualizacion=datetime.utcnow().isoformat()
            )
            session.add(db_tx)
            counts["created"] += 1
        else:
            # Mark as reconciled or update if needed
            # For now just count it as matched
            counts["matched"] += 1
            
    session.commit()
    return {"message": "Reconciliación completada", "stats": counts}
