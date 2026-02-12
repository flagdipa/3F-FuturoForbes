from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select, func
from ...core.database import get_session
from ..auth.deps import get_current_user
from ...models.models import LibroTransacciones, ListaCuentas, Usuario, Beneficiario
from ...models.models_extended import ReglaImportacion
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
    match_id: Optional[int] = None 
    match_score: float = 0.0 
    is_new: bool = True 
    id_categoria: Optional[int] = None
    new_payee: Optional[str] = None
    rule_applied: Optional[str] = None  # Name of the rule that matched

class ReconciliationProcessRequest(BaseModel):
    id_cuenta: int
    transactions: List[ReconciliationPreview]


def _apply_import_rules(session: Session, user_id: int, description: str) -> dict:
    """
    Try to match a CSV description against user's import rules.
    Returns dict with id_categoria, id_beneficiario, and rule name if matched.
    Rules are evaluated by priority descending; first match wins.
    """
    rules = session.exec(
        select(ReglaImportacion)
        .where(ReglaImportacion.id_usuario == user_id)
        .where(ReglaImportacion.activo == 1)
        .order_by(ReglaImportacion.prioridad.desc())
    ).all()

    desc_lower = description.lower()
    for rule in rules:
        if rule.patron.lower() in desc_lower:
            return {
                "id_categoria": rule.id_categoria,
                "id_beneficiario": rule.id_beneficiario,
                "rule_name": rule.patron
            }
    return {}


@router.post("/preview", response_model=List[ReconciliationPreview])
async def preview_reconciliation(
    file: UploadFile = File(...),
    id_cuenta: int = Form(...),
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Parses a CSV file and attempts to match transactions with existing records.
    For new transactions, applies import rules for auto-categorization.
    """
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un CSV")
    
    content = await file.read()
    try:
        parser = CSVParser(content)
        parsed_data = parser.parse()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not parsed_data:
        raise HTTPException(status_code=400, detail="No se encontraron transacciones válidas en el CSV")

    dates = [row['fecha'] for row in parsed_data if row.get('fecha')]
    if not dates:
        raise HTTPException(status_code=400, detail="No se pudieron detectar fechas en el CSV")
        
    min_date = min(dates)
    max_date = max(dates)
    
    existing_txs = session.exec(
        select(LibroTransacciones)
        .where(LibroTransacciones.id_cuenta == id_cuenta)
        .where(LibroTransacciones.fecha_transaccion >= min_date)
        .where(LibroTransacciones.fecha_transaccion <= max_date)
    ).all()
    
    preview_list = []
    available_txs = list(existing_txs)

    for row in parsed_data:
        csv_amount = row['monto']
        csv_date = row['fecha']
        csv_desc = row['descripcion']
        
        # Try exact match (Date + Amount)
        match = None
        for i, db_tx in enumerate(available_txs):
            if db_tx.monto_transaccion == csv_amount and db_tx.fecha_transaccion == csv_date:
                match = db_tx
                available_txs.pop(i)
                break
        
        # For new transactions, apply import rules for auto-categorization
        suggested_cat = match.id_categoria if match else None
        suggested_payee = None if match else csv_desc
        rule_name = None

        if not match:
            rule_result = _apply_import_rules(session, current_user.id_usuario, csv_desc)
            if rule_result:
                suggested_cat = rule_result.get("id_categoria") or suggested_cat
                rule_name = rule_result.get("rule_name")
                # If rule has a beneficiary, look up name for display
                if rule_result.get("id_beneficiario"):
                    benef = session.get(Beneficiario, rule_result["id_beneficiario"])
                    if benef:
                        suggested_payee = benef.nombre_beneficiario

        preview = ReconciliationPreview(
            fecha=csv_date,
            descripcion=csv_desc,
            monto=csv_amount,
            match_id=match.id_transaccion if match else None,
            match_score=100.0 if match else 0.0,
            is_new=not bool(match),
            id_categoria=suggested_cat,
            new_payee=suggested_payee,
            rule_applied=rule_name
        )
        preview_list.append(preview)
        
    return preview_list

@router.post("/process")
async def process_reconciliation(
    request: ReconciliationProcessRequest,
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Finalizes the reconciliation by creating new transactions or updating existing ones.
    Handles automatic creation of Beneficiaries with user-provided overrides.
    """
    counts = {"created": 0, "matched": 0}
    
    for tx in request.transactions:
        if tx.is_new:
            payee_name = tx.new_payee.strip().title() if tx.new_payee else tx.descripcion.strip().title()
            
            statement = select(Beneficiario).where(Beneficiario.nombre_beneficiario == payee_name)
            benef = session.exec(statement).first()
            
            if not benef:
                default_cat = tx.id_categoria if tx.id_categoria else 1
                
                benef = Beneficiario(
                    nombre_beneficiario=payee_name,
                    notas="Auto-created from Bank Import",
                    id_categoria=default_cat 
                )
                session.add(benef)
                session.commit()
                session.refresh(benef)
            
            if tx.id_categoria and tx.id_categoria > 0:
                cat_id = tx.id_categoria
            elif benef.id_categoria:
                cat_id = benef.id_categoria
            else:
                cat_id = 1

            db_tx = LibroTransacciones(
                id_cuenta=request.id_cuenta,
                fecha_transaccion=tx.fecha,
                monto_transaccion=tx.monto,
                notas=f"[Importado] {tx.descripcion}",
                id_beneficiario=benef.id_beneficiario,
                id_categoria=cat_id,
                codigo_transaccion="Withdrawal" if tx.monto < 0 else "Deposit",
                fecha_actualizacion=datetime.utcnow().isoformat()
            )
            session.add(db_tx)
            counts["created"] += 1
        else:
            counts["matched"] += 1
            
    session.commit()
    return {"message": "Reconciliación completada", "stats": counts}
