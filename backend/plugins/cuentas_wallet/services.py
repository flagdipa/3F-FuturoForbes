"""
Servicios — Plugin Cuentas / Billetera
Lógica de negocio: CRUD de entidades y tasas, comparador, historial automático.
"""
import logging
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict

import aiohttp
from sqlmodel import Session, select, func

from .models import (
    CuentasWalletEntidad,
    CuentasWalletTasa,
    CuentasWalletHistorial,
    FuenteDato,
    MonedaTasa,
)

logger = logging.getLogger("cuentas_wallet.services")

# ─── APIs públicas ────────────────────────────────────────────────────────────
API_PLAZO_FIJO = "https://api.argentinadatos.com/v1/finanzas/tasas/plazoFijo"
API_PLAZOS_FIJOS_ENTIDADES = "https://api.argentinadatos.com/v1/finanzas/tasas/plazosFijos"
API_DEPOSITOS_30 = "https://api.argentinadatos.com/v1/finanzas/tasas/depositos30Dias"


class EntidadService:
    """CRUD de wallets/fintechs."""

    @staticmethod
    def listar(session: Session, solo_activas: bool = True) -> List[CuentasWalletEntidad]:
        q = select(CuentasWalletEntidad)
        if solo_activas:
            q = q.where(CuentasWalletEntidad.activa == True)
        return session.exec(q.order_by(CuentasWalletEntidad.nombre)).all()

    @staticmethod
    def obtener(session: Session, id: int) -> Optional[CuentasWalletEntidad]:
        return session.get(CuentasWalletEntidad, id)

    @staticmethod
    def crear(session: Session, data: dict) -> CuentasWalletEntidad:
        entidad = CuentasWalletEntidad(**data)
        session.add(entidad)
        session.commit()
        session.refresh(entidad)
        return entidad

    @staticmethod
    def actualizar(session: Session, id: int, data: dict) -> Optional[CuentasWalletEntidad]:
        entidad = session.get(CuentasWalletEntidad, id)
        if not entidad:
            return None
        for k, v in data.items():
            if hasattr(entidad, k):
                setattr(entidad, k, v)
        session.add(entidad)
        session.commit()
        session.refresh(entidad)
        return entidad

    @staticmethod
    def eliminar(session: Session, id: int) -> bool:
        entidad = session.get(CuentasWalletEntidad, id)
        if not entidad:
            return False
        entidad.activa = False  # Soft delete
        session.add(entidad)
        session.commit()
        return True


class TasaService:
    """CRUD de tasas con historial automático al actualizar."""

    @staticmethod
    def listar(
        session: Session,
        id_entidad: Optional[int] = None,
        moneda: Optional[str] = None,
        solo_activas: bool = True,
    ) -> List[CuentasWalletTasa]:
        q = select(CuentasWalletTasa)
        if id_entidad:
            q = q.where(CuentasWalletTasa.id_entidad == id_entidad)
        if moneda:
            q = q.where(CuentasWalletTasa.moneda == moneda)
        if solo_activas:
            q = q.where(CuentasWalletTasa.activa == True)
        return session.exec(q.order_by(CuentasWalletTasa.valor.desc())).all()

    @staticmethod
    def crear(session: Session, data: dict) -> CuentasWalletTasa:
        tasa = CuentasWalletTasa(**data)
        session.add(tasa)
        session.commit()
        session.refresh(tasa)
        return tasa

    @staticmethod
    def actualizar(session: Session, id: int, data: dict) -> Optional[CuentasWalletTasa]:
        tasa = session.get(CuentasWalletTasa, id)
        if not tasa:
            return None

        # Guardar historial si el valor cambió
        nuevo_valor = data.get("valor")
        if nuevo_valor is not None and Decimal(str(nuevo_valor)) != tasa.valor:
            hist = CuentasWalletHistorial(
                id_tasa=tasa.id,
                id_entidad=tasa.id_entidad,
                tipo_producto=tasa.tipo_producto,
                moneda=tasa.moneda,
                valor_anterior=tasa.valor,
                valor_nuevo=Decimal(str(nuevo_valor)),
                variacion=Decimal(str(nuevo_valor)) - tasa.valor,
                fuente=data.get("fuente", FuenteDato.MANUAL),
            )
            session.add(hist)

        for k, v in data.items():
            if hasattr(tasa, k):
                setattr(tasa, k, v)
        tasa.actualizado_el = datetime.utcnow()
        session.add(tasa)
        session.commit()
        session.refresh(tasa)
        return tasa

    @staticmethod
    def eliminar(session: Session, id: int) -> bool:
        tasa = session.get(CuentasWalletTasa, id)
        if not tasa:
            return False
        tasa.activa = False
        session.add(tasa)
        session.commit()
        return True


class ComparadorService:
    """Comparación de tasas entre entidades."""

    @staticmethod
    def comparar(
        session: Session,
        moneda: str = "ARS",
        tipo_producto: Optional[str] = None,
    ) -> List[dict]:
        """
        Retorna ranking de tasas ordenado de mayor a menor,
        enriquecido con datos de la entidad.
        """
        q = (
            select(CuentasWalletTasa, CuentasWalletEntidad)
            .join(
                CuentasWalletEntidad,
                CuentasWalletTasa.id_entidad == CuentasWalletEntidad.id,
            )
            .where(
                CuentasWalletTasa.activa == True,
                CuentasWalletTasa.moneda == moneda,
                CuentasWalletEntidad.activa == True,
            )
        )
        if tipo_producto:
            q = q.where(CuentasWalletTasa.tipo_producto == tipo_producto)
        q = q.order_by(CuentasWalletTasa.valor.desc())

        resultados = []
        for idx, (tasa, entidad) in enumerate(session.exec(q).all(), start=1):
            resultados.append(
                {
                    "posicion": idx,
                    "entidad": {
                        "id": entidad.id,
                        "nombre": entidad.nombre,
                        "nombre_corto": entidad.nombre_corto,
                        "tipo": entidad.tipo,
                        "color_hex": entidad.color_hex,
                        "url_logo": entidad.url_logo,
                    },
                    "tasa": {
                        "id": tasa.id,
                        "tipo_producto": tasa.tipo_producto,
                        "tipo_tasa": tasa.tipo_tasa,
                        "valor": float(tasa.valor),
                        "valor_tea": float(tasa.valor_tea) if tasa.valor_tea else None,
                        "moneda": tasa.moneda,
                        "plazo_dias": tasa.plazo_dias,
                        "monto_minimo": float(tasa.monto_minimo) if tasa.monto_minimo else None,
                        "condiciones": tasa.condiciones,
                        "fuente": tasa.fuente,
                        "actualizado_el": tasa.actualizado_el.isoformat(),
                    },
                }
            )
        return resultados

    @staticmethod
    def historial_entidad(
        session: Session, id_entidad: int, limite: int = 30
    ) -> List[dict]:
        """Historial de cambios de tasas para una entidad."""
        registros = session.exec(
            select(CuentasWalletHistorial)
            .where(CuentasWalletHistorial.id_entidad == id_entidad)
            .order_by(CuentasWalletHistorial.registrado_el.desc())
            .limit(limite)
        ).all()
        return [
            {
                "producto": r.tipo_producto,
                "moneda": r.moneda,
                "anterior": float(r.valor_anterior),
                "nuevo": float(r.valor_nuevo),
                "variacion": float(r.variacion),
                "fecha": r.registrado_el.isoformat(),
            }
            for r in registros
        ]


class SyncService:
    """Sincronización automática con APIs públicas (ArgentinaDatos)."""

    @staticmethod
    async def sincronizar_plazo_fijo(session: Session) -> dict:
        """
        Actualiza tasas de plazo fijo desde argentinadatos.com.
        Crea entidades automáticamente si no existen.
        """
        resultado = {"actualizadas": 0, "creadas": 0, "errores": []}
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15)
            ) as http:
                async with http.get(API_PLAZOS_FIJOS_ENTIDADES) as resp:
                    if resp.status != 200:
                        return {"error": f"HTTP {resp.status}"}
                    datos = await resp.json()

            for item in datos:
                try:
                    nombre_entidad = item.get("entidad", "").strip()
                    tna = item.get("tnaClientes") or item.get("tna") or 0
                    if not nombre_entidad or not tna:
                        continue

                    tna_decimal = Decimal(str(tna))
                    tea = _tna_a_tea(tna_decimal)

                    # Buscar o crear entidad
                    entidad = session.exec(
                        select(CuentasWalletEntidad).where(
                            CuentasWalletEntidad.nombre.ilike(f"%{nombre_entidad}%")
                        )
                    ).first()

                    if not entidad:
                        entidad = CuentasWalletEntidad(
                            nombre=nombre_entidad,
                            nombre_corto=nombre_entidad[:20],
                            tipo="Banco",
                        )
                        session.add(entidad)
                        session.flush()
                        resultado["creadas"] += 1

                    # Buscar tasa existente de PF en ARS
                    tasa = session.exec(
                        select(CuentasWalletTasa).where(
                            CuentasWalletTasa.id_entidad == entidad.id,
                            CuentasWalletTasa.tipo_producto == "Plazo Fijo",
                            CuentasWalletTasa.moneda == MonedaTasa.ARS,
                        )
                    ).first()

                    if tasa:
                        # Guardar historial si cambió
                        if tasa.valor != tna_decimal:
                            hist = CuentasWalletHistorial(
                                id_tasa=tasa.id,
                                id_entidad=entidad.id,
                                tipo_producto="Plazo Fijo",
                                moneda="ARS",
                                valor_anterior=tasa.valor,
                                valor_nuevo=tna_decimal,
                                variacion=tna_decimal - tasa.valor,
                                fuente=FuenteDato.API,
                            )
                            session.add(hist)
                            tasa.valor = tna_decimal
                            tasa.valor_tea = tea
                            tasa.actualizado_el = datetime.utcnow()
                            tasa.fuente = FuenteDato.API
                            session.add(tasa)
                        resultado["actualizadas"] += 1
                    else:
                        nueva = CuentasWalletTasa(
                            id_entidad=entidad.id,
                            tipo_producto="Plazo Fijo",
                            moneda=MonedaTasa.ARS,
                            valor=tna_decimal,
                            valor_tea=tea,
                            plazo_dias=30,
                            fuente=FuenteDato.API,
                            url_fuente=API_PLAZOS_FIJOS_ENTIDADES,
                        )
                        session.add(nueva)
                        resultado["actualizadas"] += 1

                except Exception as e:
                    resultado["errores"].append(str(e))

            session.commit()
        except Exception as e:
            logger.error(f"Error sincronizando plazo fijo: {e}")
            resultado["error"] = str(e)

        return resultado


def _tna_a_tea(tna: Decimal, dias: int = 365) -> Decimal:
    """Convierte TNA a TEA con capitalización diaria."""
    try:
        from decimal import Decimal as D
        tasa_diaria = tna / D("100") / D(str(dias))
        tea = ((1 + tasa_diaria) ** dias - 1) * D("100")
        return tea.quantize(D("0.0001"))
    except Exception:
        return Decimal("0")
