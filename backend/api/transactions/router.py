from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from ...core.database import get_session, get_current_user
from ...core.audit_service import audit_service
from ...models.models import LibroTransacciones, TransaccionDividida, ListaCuentas, Beneficiario, Categoria, Usuario
from .schemas import TransaccionCrear, TransaccionLectura, TransaccionComplejaCrear, DivisionCrear
from backend.models.models_extended import TransaccionEtiqueta
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/transacciones", tags=["Transacciones"])

def _enriquecer_transaccion(tx: LibroTransacciones, session: Session) -> TransaccionLectura:
    tx_lectura = TransaccionLectura.from_orm(tx)
    
    cuenta = session.get(ListaCuentas, tx.id_cuenta)
    if cuenta: tx_lectura.nombre_cuenta = cuenta.nombre_cuenta
    
    benef = session.get(Beneficiario, tx.id_beneficiario)
    if benef: tx_lectura.nombre_beneficiario = benef.nombre_beneficiario
    
    cat = session.get(Categoria, tx.id_categoria)
    if cat: tx_lectura.nombre_categoria = cat.nombre_categoria
    
    # Cargar IDs de etiquetas
    ids_etiquetas = session.exec(
        select(TransaccionEtiqueta.id_etiqueta)
        .where(TransaccionEtiqueta.id_transaccion == tx.id_transaccion)
    ).all()
    tx_lectura.etiquetas = ids_etiquetas
    
    return tx_lectura

@router.get("/", response_model=List[TransaccionLectura])
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
    query = select(LibroTransacciones)
    
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
        # Búsqueda en notas y número de transacción
        query = query.where(
            (LibroTransacciones.notas.contains(busqueda)) | 
            (LibroTransacciones.numero_transaccion.contains(busqueda))
        )
        
    query = query.order_by(LibroTransacciones.id_transaccion.desc()).offset(offset).limit(limit)
    results = session.exec(query).all()
    
    return [_enriquecer_transaccion(tx, session) for tx in results]

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
        session.commit()

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
        session.commit()
    else:
        # Si dejó de ser dividida, borrar cualquier rastro
        viejas = session.exec(
            select(TransaccionDividida)
            .where(TransaccionDividida.id_transaccion == tx_id)
        ).all()
        for v in viejas:
            session.delete(v)
        session.commit()

    session.refresh(db_tx)
    return _enriquecer_transaccion(db_tx, session)

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
def crear_transaccion(
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
    session.commit()
    session.refresh(db_tx)
    
    # Log creation
    audit_service.log(session, current_user.id_usuario, "CREATE", "Transaccion", db_tx.id_transaccion, tx_in.dict(exclude={"divisiones", "etiquetas"}))
    
    # Gestionar Etiquetas (M:N)
    if tx_in.etiquetas:
        for tag_id in tx_in.etiquetas:
            session.add(TransaccionEtiqueta(id_transaccion=db_tx.id_transaccion, id_etiqueta=tag_id))
        session.commit()
    
    if tx_in.es_dividida and tx_in.divisiones:
        for split in tx_in.divisiones:
            db_split = TransaccionDividida(
                id_transaccion=db_tx.id_transaccion,
                id_categoria=split.id_categoria,
                monto_division=split.monto_division,
                notas=split.notas
            )
            session.add(db_split)
        session.commit()
        
    session.refresh(db_tx)
    
    # Notify about high value transaction
    if db_tx.monto_transaccion >= 1000:
        from ..notifications.router import notify_info
        import asyncio
        asyncio.create_task(notify_info(
            user_id=current_user.id_usuario,
            title="Transacción Elevada",
            message=f"Se ha registrado una transacción de {db_tx.monto_transaccion} en la cuenta."
        ))
        
    return _enriquecer_transaccion(db_tx, session)

@router.delete("/{tx_id}")
def eliminar_transaccion(
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
    import asyncio
    asyncio.create_task(notify_warning(
        user_id=current_user.id_usuario,
        title="Transacción Eliminada",
        message=f"Se ha eliminado una transacción del historial."
    ))
    
    return {"message": "Transacción eliminada"}

