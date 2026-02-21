from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...core.database import get_session
from ..auth.deps import get_current_user
from ...core.audit_service import audit_service
from ...core.plugin_manager import plugin_manager
from ...models.models import LibroTransacciones, TransaccionDividida, ListaCuentas, Beneficiario, Categoria, Usuario
from .schemas import TransaccionCrear, TransaccionLectura, TransaccionComplejaCrear, DivisionCrear
from backend.models.models_extended import TransaccionEtiqueta
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/transacciones", tags=["Transacciones"])

from sqlalchemy.orm import joinedload
from sqlalchemy import func
from ..schemas.common import PaginatedResponse, PaginationMetadata

def _enriquecer_rapido(tx: LibroTransacciones, tags: List[int]) -> TransaccionLectura:
    """Enrich transaction data using eager-loaded relationships and pre-fetched tags"""
    tx_lectura = TransaccionLectura.from_orm(tx)
    
    if tx.cuenta:
        tx_lectura.nombre_cuenta = tx.cuenta.nombre_cuenta
    if tx.beneficiario:
        tx_lectura.nombre_beneficiario = tx.beneficiario.nombre_beneficiario
    if tx.categoria:
        tx_lectura.nombre_categoria = tx.categoria.nombre_categoria
    
    tx_lectura.etiquetas = tags
    return tx_lectura

@router.get("/", response_model=PaginatedResponse[TransaccionLectura])
def listar_transacciones(
    offset: int = 0, 
    limit: int = 100, 
    id_cuenta: Optional[int] = None,
    id_beneficiario: Optional[int] = None,
    id_categoria: Optional[int] = None,
    id_etiqueta: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    busqueda: Optional[str] = None,
    moneda: Optional[str] = None,
    session: Session = Depends(get_session)
):
    # Build a separate count query (no joinedload — avoids subquery issues)
    count_query = select(func.count()).select_from(LibroTransacciones)

    # Base query with eager loading
    query = (
        select(LibroTransacciones)
        .options(
            joinedload(LibroTransacciones.cuenta),
            joinedload(LibroTransacciones.beneficiario),
            joinedload(LibroTransacciones.categoria)
        )
    )
    
    if id_etiqueta:
        query = query.join(TransaccionEtiqueta, LibroTransacciones.id_transaccion == TransaccionEtiqueta.id_transaccion)\
                     .where(TransaccionEtiqueta.id_etiqueta == id_etiqueta)
        count_query = count_query.join(TransaccionEtiqueta, LibroTransacciones.id_transaccion == TransaccionEtiqueta.id_transaccion)\
                                 .where(TransaccionEtiqueta.id_etiqueta == id_etiqueta)

    if moneda:
        # Filter by currency joining with ListaCuentas and Divisa
        from ...models.models import Divisa
        query = query.join(ListaCuentas, LibroTransacciones.id_cuenta == ListaCuentas.id_cuenta)\
                     .join(Divisa, ListaCuentas.id_divisa == Divisa.id_divisa)\
                     .where(Divisa.codigo_iso == moneda)
        count_query = count_query.join(ListaCuentas, LibroTransacciones.id_cuenta == ListaCuentas.id_cuenta)\
                                 .join(Divisa, ListaCuentas.id_divisa == Divisa.id_divisa)\
                                 .where(Divisa.codigo_iso == moneda)
        
    if id_cuenta:
        query = query.where(LibroTransacciones.id_cuenta == id_cuenta)
        count_query = count_query.where(LibroTransacciones.id_cuenta == id_cuenta)
        
    if id_beneficiario:
        query = query.where(LibroTransacciones.id_beneficiario == id_beneficiario)
        count_query = count_query.where(LibroTransacciones.id_beneficiario == id_beneficiario)
        
    if id_categoria:
        query = query.where(LibroTransacciones.id_categoria == id_categoria)
        count_query = count_query.where(LibroTransacciones.id_categoria == id_categoria)
    if fecha_inicio:
        query = query.where(LibroTransacciones.fecha_transaccion >= fecha_inicio)
        count_query = count_query.where(LibroTransacciones.fecha_transaccion >= fecha_inicio)
    if fecha_fin:
        query = query.where(LibroTransacciones.fecha_transaccion <= fecha_fin)
        count_query = count_query.where(LibroTransacciones.fecha_transaccion <= fecha_fin)
    if busqueda:
        query = query.where(
            (LibroTransacciones.notas.contains(busqueda)) | 
            (LibroTransacciones.numero_transaccion.contains(busqueda))
        )
        count_query = count_query.where(
            (LibroTransacciones.notas.contains(busqueda)) | 
            (LibroTransacciones.numero_transaccion.contains(busqueda))
        )
    
    # Calculate total using the dedicated count query
    total = session.exec(count_query).one()
        
    # Apply ordering and pagination
    query = query.order_by(LibroTransacciones.id_transaccion.desc()).offset(offset).limit(limit)
    results = session.exec(query).all()
    
    # Batch load labels for all transactions in one query
    tx_ids = [tx.id_transaccion for tx in results]
    tags_by_tx = {}
    if tx_ids:
        all_tags = session.exec(
            select(TransaccionEtiqueta)
            .where(TransaccionEtiqueta.id_transaccion.in_(tx_ids))
        ).all()
        for tag in all_tags:
            tags_by_tx.setdefault(tag.id_transaccion, []).append(tag.id_etiqueta)
    
    # Calculate Running Balance if filtered by account
    from decimal import Decimal
    running_balances = {}
    
    if id_cuenta and results:
        account = session.get(ListaCuentas, id_cuenta)
        initial_balance = account.saldo_inicial if account else Decimal(0)
        total_sum_query = select(func.sum(LibroTransacciones.monto_transaccion)).where(LibroTransacciones.id_cuenta == id_cuenta)
        total_sum = session.exec(total_sum_query).one() or Decimal(0)
        current_balance = initial_balance + total_sum
        newest_id_in_page = results[0].id_transaccion
        future_sum_query = select(func.sum(LibroTransacciones.monto_transaccion)).where(
            LibroTransacciones.id_cuenta == id_cuenta,
            LibroTransacciones.id_transaccion > newest_id_in_page
        )
        future_sum = session.exec(future_sum_query).one() or Decimal(0)
        starting_balance = current_balance - future_sum
        current_iter_balance = starting_balance
        for tx in results:
            running_balances[tx.id_transaccion] = current_iter_balance
            current_iter_balance = current_iter_balance - tx.monto_transaccion

    data = []
    for tx in results:
        enriched = _enriquecer_rapido(tx, tags_by_tx.get(tx.id_transaccion, []))
        if tx.id_transaccion in running_balances:
            enriched.saldo = running_balances[tx.id_transaccion]
        data.append(enriched)
    
    return PaginatedResponse(
        data=data,
        pagination=PaginationMetadata(
            total=total,
            offset=offset,
            limit=limit,
            has_more=(offset + limit) < total
        )
    )

@router.put("/{tx_id}", response_model=TransaccionLectura)
def actualizar_transaccion(
    tx_id: int, 
    tx_in: TransaccionComplejaCrear, 
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    db_tx = session.get(LibroTransacciones, tx_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    tx_data = tx_in.dict(exclude_unset=True, exclude={"divisiones", "etiquetas"})
        
    for key, value in tx_data.items():
        setattr(db_tx, key, value)
    
    db_tx.fecha_actualizacion = datetime.utcnow().isoformat()
    session.add(db_tx)
    
    # Log update
    audit_service.log(session, current_user.id_usuario, "UPDATE", "Transaccion", tx_id, tx_in.dict(exclude={"divisiones", "etiquetas"}))
    
    session.commit()
    
    # Actualizar Etiquetas (M:N)
    if tx_in.etiquetas is not None:
        previas = session.exec(select(TransaccionEtiqueta).where(TransaccionEtiqueta.id_transaccion == tx_id)).all()
        for p in previas: session.delete(p)
        for tag_id in tx_in.etiquetas:
            session.add(TransaccionEtiqueta(id_transaccion=tx_id, id_etiqueta=tag_id))

    # Actualizar Divisiones
    if tx_in.es_dividida:
        viejas = session.exec(select(TransaccionDividida).where(TransaccionDividida.id_transaccion == tx_id)).all()
        for v in viejas: session.delete(v)
        if tx_in.divisiones:
            for split in tx_in.divisiones:
                db_split = TransaccionDividida(
                    id_transaccion=tx_id,
                    id_categoria=split.id_categoria,
                    monto_division=split.monto_division,
                    notas=split.notas
                )
                session.add(db_split)
    else:
        viejas = session.exec(select(TransaccionDividida).where(TransaccionDividida.id_transaccion == tx_id)).all()
        for v in viejas: session.delete(v)

    session.commit()
    session.refresh(db_tx)
    tags_query = select(TransaccionEtiqueta.id_etiqueta).where(TransaccionEtiqueta.id_transaccion == tx_id)
    tags = session.exec(tags_query).all()
    return _enriquecer_rapido(db_tx, tags)

@router.get("/{tx_id}/divisiones", response_model=List[DivisionCrear])
def obtener_divisiones_transaccion(tx_id: int, session: Session = Depends(get_session)):
    splits = session.exec(select(TransaccionDividida).where(TransaccionDividida.id_transaccion == tx_id)).all()
    return [DivisionCrear(id_categoria=s.id_categoria, monto_division=s.monto_division, notas=s.notas) for s in splits]

@router.post("/", response_model=TransaccionLectura)
async def crear_transaccion(
    tx_in: TransaccionComplejaCrear, 
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    cuenta_origen = session.get(ListaCuentas, tx_in.id_cuenta)
    if not cuenta_origen:
        raise HTTPException(status_code=404, detail="Cuenta de origen no encontrada")
    
    tx_data = tx_in.dict(exclude={"divisiones", "etiquetas"})
    db_tx = LibroTransacciones(**tx_data)
    db_tx.fecha_actualizacion = datetime.utcnow().isoformat()
    if not db_tx.fecha_transaccion:
        db_tx.fecha_transaccion = datetime.utcnow().isoformat()
        
    session.add(db_tx)
    session.flush()
    
    audit_service.log(session, current_user.id_usuario, "CREATE", "Transaccion", db_tx.id_transaccion, tx_in.dict(exclude={"divisiones", "etiquetas"}))
    
    tags = []
    if tx_in.etiquetas:
        for tag_id in tx_in.etiquetas:
            session.add(TransaccionEtiqueta(id_transaccion=db_tx.id_transaccion, id_etiqueta=tag_id))
            tags.append(tag_id)
    
    if tx_in.es_dividida and tx_in.divisiones:
        for split in tx_in.divisiones:
            db_split = TransaccionDividida(id_transaccion=db_tx.id_transaccion, id_categoria=split.id_categoria, monto_division=split.monto_division, notas=split.notas)
            session.add(db_split)
    
    session.commit()
    session.refresh(db_tx)
    await plugin_manager.call_hook("transaction_created", transaction=db_tx, user=current_user)
    return _enriquecer_rapido(db_tx, tags)

@router.delete("/{tx_id}")
async def eliminar_transaccion(
    tx_id: int, 
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    db_tx = session.get(LibroTransacciones, tx_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    audit_service.log(session, current_user.id_usuario, "DELETE", "Transaccion", tx_id, {"monto": float(db_tx.monto_transaccion)})
    session.delete(db_tx)
    session.commit()
    return {"message": "Transacción eliminada"}
