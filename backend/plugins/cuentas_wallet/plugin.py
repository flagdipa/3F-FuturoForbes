"""
Plugin Cuentas / Billetera — v1.1.0
Gestión y comparación de tasas de interés de wallets y fintechs argentinas.
"""
import logging
from sqlmodel import SQLModel
from backend.plugins.base import BasePlugin
from backend.core.database import engine

logger = logging.getLogger("cuentas_wallet")


class CuentasWalletPlugin(BasePlugin):
    technical_name = "cuentas_wallet"
    display_name = "Cuentas / Billetera"
    version = "1.1.0"
    autor = "3F Labs"
    descripcion = (
        "Comparativa de tasas de interés de bancos, fintechs y billeteras virtuales "
        "argentinas. Soporta: Plazo Fijo, Cuenta Remunerada, FCI. "
        "Sincroniza automáticamente con argentinadatos.com."
    )
    hooks = ["daily_summary", "system_periodic_sync"]

    async def initialize(self):
        # Crear tablas del plugin si no existen
        from backend.plugins.cuentas_wallet.models import (
            CuentasWalletEntidad,
            CuentasWalletTasa,
            CuentasWalletHistorial,
        )
        SQLModel.metadata.create_all(engine)
        self.logger.info(f"✅ {self.display_name} inicializado — tablas creadas")

        # Cargar entidades de ejemplo si la tabla está vacía
        try:
            from sqlmodel import Session, select
            from backend.plugins.cuentas_wallet.models import CuentasWalletEntidad
            with Session(engine) as session:
                count = len(session.exec(select(CuentasWalletEntidad)).all())
                if count == 0:
                    self.logger.info("Cargando entidades de ejemplo...")
                    await self._seed_entidades(session)
        except Exception as e:
            self.logger.warning(f"No se pudo hacer seed inicial: {e}")

    async def shutdown(self):
        self.logger.info(f"{self.display_name} desactivado")

    async def on_daily_summary(self, **kwargs):
        """Sincronización diaria de tasas desde APIs públicas."""
        await self._sync_all()

    async def on_system_periodic_sync(self, **kwargs):
        """Sincronización periódica — evita duplicar si ya hay datos de hoy."""
        from sqlmodel import Session, select
        from datetime import datetime, date
        from backend.plugins.cuentas_wallet.models import CuentasWalletHistorial
        with Session(engine) as session:
            hoy = date.today()
            existe = session.exec(
                select(CuentasWalletHistorial).where(
                    CuentasWalletHistorial.registrado_el >= datetime.combine(
                        hoy, datetime.min.time()
                    )
                )
            ).first()
            if not existe:
                await self._sync_all()

    async def _sync_all(self):
        """Ejecuta todas las sincronizaciones configuradas."""
        from sqlmodel import Session
        from backend.plugins.cuentas_wallet.services import SyncService
        sources = self.config.get("sources", ["plazo_fijo"])
        with Session(engine) as session:
            if "plazo_fijo" in sources:
                result = await SyncService.sincronizar_plazo_fijo(session)
                self.logger.info(
                    f"Sync Plazo Fijo: {result.get('actualizadas', 0)} actualizadas, "
                    f"{result.get('creadas', 0)} nuevas"
                )

    async def _seed_entidades(self, session):
        """Entidades de ejemplo al inicializar por primera vez."""
        from backend.plugins.cuentas_wallet.models import CuentasWalletEntidad, CuentasWalletTasa, MonedaTasa, FuenteDato
        from decimal import Decimal
        entidades = [
            CuentasWalletEntidad(nombre="Mercado Pago", nombre_corto="MP", tipo="Billetera Virtual", color_hex="#009EE3"),
            CuentasWalletEntidad(nombre="Ualá", nombre_corto="Uala", tipo="Billetera Virtual", color_hex="#7B2FBE"),
            CuentasWalletEntidad(nombre="Lemon Cash", nombre_corto="Lemon", tipo="Fintech Crypto", color_hex="#F5FF67"),
            CuentasWalletEntidad(nombre="Buenbit", nombre_corto="Buenbit", tipo="Exchange Crypto", color_hex="#FF6B2B"),
            CuentasWalletEntidad(nombre="Banco Nación", nombre_corto="BNA", tipo="Banco", color_hex="#007AC3"),
        ]
        for e in entidades:
            session.add(e)
        session.flush()
        self.logger.info(f"Seed: {len(entidades)} entidades creadas")
        session.commit()

    def get_config_schema(self) -> dict:
        """Schema de configuración para el modal de plugins."""
        return {
            "type": "object",
            "properties": {
                "sources": {
                    "type": "array",
                    "title": "Fuentes de sincronización",
                    "items": {"type": "string", "enum": ["plazo_fijo"]},
                    "default": ["plazo_fijo"],
                },
                "sync_interval_hours": {
                    "type": "integer",
                    "title": "Intervalo de sincronización (horas)",
                    "default": 24,
                    "minimum": 1,
                    "maximum": 168,
                },
            },
        }
