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
    session: Session = Depends(get_session)
):
    # Base query with eager loading
    query = (
        select(LibroTransacciones)
        .options(
            joinedload(LibroTransacciones.cuenta),
            joinedload(LibroTransacciones.beneficiario),
            joinedload(LibroTransacciones.categoria)
        )
    )
    
    # Filter by user if possible (assuming id_usuario exists in schema)
    # query = query.where(LibroTransacciones.id_usuario == current_user.id_usuario)
    
    if id_etiqueta:
        query = query.join(TransaccionEtiqueta, LibroTransacciones.id_transaccion == TransaccionEtiqueta.id_transaccion)\
                     .where(TransaccionEtiqueta.id_etiqueta == id_etiqueta)
        
    if id_cuenta:
        query = query.where(LibroTransacciones.id_cuenta == id_cuenta)
    if id_beneficiario:
        query = query.where(LibroTransacciones.id_beneficiario == id_beneficiario)
    if id_categoria:
        query = query.where(LibroTransacciones.id_categoria == id_categoria)
    if fecha_inicio:
        query = query.where(LibroTransacciones.fecha_transaccion >= fecha_inicio)
    if fecha_fin:
        query = query.where(LibroTransacciones.fecha_transaccion <= fecha_fin)
    if busqueda:
        query = query.where(
            (LibroTransacciones.notas.contains(busqueda)) | 
            (LibroTransacciones.numero_transaccion.contains(busqueda))
        )
    
    # Calculate total before limit/offset
    total_query = select(func.count()).select_from(query.subquery())
    total = session.exec(total_query).one()
        
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
    
    # Only calculate if filtering by a single account and utilizing default sort (ID DESC)
    # Ideally should check for sort params if/when implemented
    if id_cuenta and results:
        # 1. Get Account Initial Balance
        from ...models.models import ListaCuentas
        account = session.get(ListaCuentas, id_cuenta)
        initial_balance = account.saldo_inicial if account else Decimal(0)

        # 2. Get Sum of ALL transactions for this account (Total Current Balance)
        total_sum_query = select(func.sum(LibroTransacciones.monto_transaccion)).where(LibroTransacciones.id_cuenta == id_cuenta)
        total_sum = session.exec(total_sum_query).one() or Decimal(0)
        current_balance = initial_balance + total_sum

        # 3. Calculate "Future" movement (transactions newer than the first one in this page)
        newest_id_in_page = results[0].id_transaccion
        
        future_sum_query = select(func.sum(LibroTransacciones.monto_transaccion)).where(
            LibroTransacciones.id_cuenta == id_cuenta,
            LibroTransacciones.id_transaccion > newest_id_in_page
        )
        future_sum = session.exec(future_sum_query).one() or Decimal(0)

        # 4. Determine Balance for the first row (Top of page)
        # Balance After Row 0 = Total Balance - (Sum of transactions that happened AFTER Row 0)
        starting_balance = current_balance - future_sum
        
        # 5. Iterate and assign downwards
        current_iter_balance = starting_balance
        for tx in results:
            running_balances[tx.id_transaccion] = current_iter_balance
            # Balance(Previous/Older) = Balance(Current) - Amount(Current)
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
        # Borrar previas
        previas = session.exec(
            select(TransaccionEtiqueta)
            .where(TransaccionEtiqueta.id_transaccion == tx_id)
        ).all()
        for p in previas:
            session.delete(p)
        
        # Agregar nuevas
        for tag_id in tx_in.etiquetas:
            session.add(TransaccionEtiqueta(id_transaccion=tx_id, id_etiqueta=tag_id))

    # Actualizar Divisiones si corresponde
    if tx_in.es_dividida:
        # Borrar previas
        viejas = session.exec(
            select(TransaccionDividida)
            .where(TransaccionDividida.id_transaccion == tx_id)
        ).all()
        for v in viejas:
            session.delete(v)
        
        # Agregar nuevas
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
        # Si dejó de ser dividida, borrar cualquier rastro
        viejas = session.exec(
            select(TransaccionDividida)
            .where(TransaccionDividida.id_transaccion == tx_id)
        ).all()
        for v in viejas:
            session.delete(v)

    # UN SOLO COMMIT AL FINAL
    session.commit()
    session.refresh(db_tx)
    
    # Recargar etiquetas para el enriquecimiento
    tags_query = select(TransaccionEtiqueta.id_etiqueta).where(TransaccionEtiqueta.id_transaccion == tx_id)
    tags = session.exec(tags_query).all()
    
    return _enriquecer_rapido(db_tx, tags)

@router.get("/{tx_id}/divisiones", response_model=List[DivisionCrear])
def obtener_divisiones_transaccion(tx_id: int, session: Session = Depends(get_session)):
    """Obtiene el desglose de una transacción dividida"""
    splits = session.exec(
        select(TransaccionDividida)
        .where(TransaccionDividida.id_transaccion == tx_id)
    ).all()
    
    # Mapear a schema de salida (DivisionCrear es compatible)
    return [DivisionCrear(
        id_categoria=s.id_categoria,
        monto_division=s.monto_division,
        notas=s.notas
    ) for s in splits]

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
    # Flush to get the ID without committing yet
    session.flush()
    
    # Log creation
    audit_service.log(session, current_user.id_usuario, "CREATE", "Transaccion", db_tx.id_transaccion, tx_in.dict(exclude={"divisiones", "etiquetas"}))
    
    # Gestionar Etiquetas (M:N)
    tags = []
    if tx_in.etiquetas:
        for tag_id in tx_in.etiquetas:
            session.add(TransaccionEtiqueta(id_transaccion=db_tx.id_transaccion, id_etiqueta=tag_id))
            tags.append(tag_id)
    
    if tx_in.es_dividida and tx_in.divisiones:
        for split in tx_in.divisiones:
            db_split = TransaccionDividida(
                id_transaccion=db_tx.id_transaccion,
                id_categoria=split.id_categoria,
                monto_division=split.monto_division,
                notas=split.notas
            )
            session.add(db_split)
    
    # UN SOLO COMMIT AL FINAL
    session.commit()
    session.refresh(db_tx)
    
    # Disparar hook de plugin
    await plugin_manager.call_hook(
        "transaction_created",
        transaction=db_tx,
        user=current_user
    )
    
    # Notify about high value transaction (post-commit)
    if db_tx.monto_transaccion >= 1000:
        from ..notifications.router import notify_info
        await notify_info(
            user_id=current_user.id_usuario,
            title="Transacción Elevada",
            message=f"Se ha registrado una transacción de {db_tx.monto_transaccion} en la cuenta.",
            session=session
        )
        
    return _enriquecer_rapido(db_tx, tags)

@router.delete("/{tx_id}")
async def eliminar_transaccion(
    tx_id: int, 
    session: Session = Depends(get_session),
    current_user: Usuario = Depends(get_current_user)
):
    """Elimina una transacción y sus dependencias (divisiones, etiquetas)"""
    db_tx = session.get(LibroTransacciones, tx_id)
    if not db_tx:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    
    # Log deletion
    audit_service.log(session, current_user.id_usuario, "DELETE", "Transaccion", tx_id, {"monto": float(db_tx.monto_transaccion)})
    
    session.delete(db_tx)
    session.commit()
    
    # Notify about deletion
    from ..notifications.router import notify_warning
    await notify_warning(
        user_id=current_user.id_usuario,
        title="Transacción Eliminada",
        message=f"Se ha eliminado una transacción del historial.",
        session=session
    )
    
    return {"message": "Transacción eliminada"}

