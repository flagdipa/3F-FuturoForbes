import aiohttp
from datetime import datetime
from typing import Dict, Any, List, Optional
from backend.plugins.base import BasePlugin
from sqlmodel import Session, select, SQLModel, Field, Column, JSON
from backend.core.database import engine

class CuentasWalletRateHist(SQLModel, table=True):
    __tablename__ = "cuentaswallet_tasas_hist"
    id: Optional[int] = Field(default=None, primary_key=True)
    entidad: str = Field(index=True)
    tipo: str = Field(index=True) # plazo_fijo, cuenta_remunerada
    tna: float
    tea: float = 0.0
    fecha: datetime = Field(default_factory=datetime.utcnow)

class CuentasWalletPlugin(BasePlugin):
    """
    Plugin para comparar tasas de interés de bancos y billeteras virtuales.
    """
    nombre_tecnico = "cuentas_wallet"
    nombre_display = "Cuentas / Billetera"
    version = "1.0.0"
    autor = "3F Labs"
    descripcion = "Comparativa de tasas de interés (Plazo Fijo vs Cuentas Remuneradas)."
    hooks = ["dashboard_charts", "system_periodic_sync"]

    API_PLAZO_FIJO = "https://api.argentinadatos.com/v1/finanzas/tasas/plazoFijo"
    API_CUENTAS_REM = "https://api.argentinadatos.com/v1/finanzas/fci/otros/ultimo"

    async def initialize(self):
        SQLModel.metadata.create_all(engine)
        self.logger.info(f"{self.nombre_display} inicializado")

    async def shutdown(self):
        self.logger.info(f"{self.nombre_display} apagado")

    async def get_comparison_data(self) -> Dict[str, List[Any]]:
        """
        Obtiene datos de plazos fijos y cuentas remuneradas para comparar según configuración
        """
        results = {"plazos_fijos": [], "cuentas_remuneradas": []}
        opts = self.config.get("compare_options", {})
        
        async with aiohttp.ClientSession() as session:
            # 1. Fetch Plazos Fijos if enabled
            if opts.get("fixed_terms", True):
                try:
                    async with session.get(self.API_PLAZO_FIJO) as resp:
                        if resp.status == 200:
                            results["plazos_fijos"] = await resp.json()
                except Exception as e:
                    self.logger.error(f"Error fetching pf: {e}")

            # 2. Fetch Cuentas Remuneradas (FCI Otros) if enabled
            if opts.get("wallets", True):
                try:
                    async with session.get(self.API_CUENTAS_REM) as resp:
                        if resp.status == 200:
                            results["cuentas_remuneradas"] = await resp.json()
                except Exception as e:
                    self.logger.error(f"Error fetching accounts: {e}")

        return results

    async def save_rates_to_hist(self):
        """Persistir tasas actuales al historial para gráficos futuros"""
        data = await self.get_comparison_data()
        with Session(engine) as session:
            # Guardar Top 5 plazos fijos
            for pf in sorted(data["plazos_fijos"], key=lambda x: (x.get("tnaClientes") or 0.0), reverse=True)[:5]:
                hist = CuentasWalletRateHist(
                    entidad=pf["entidad"],
                    tipo="plazo_fijo",
                    tna=pf.get("tnaClientes", 0)
                )
                session.add(hist)
            
            # Guardar Top 5 cuentas remuneradas
            for acc in sorted(data["cuentas_remuneradas"], key=lambda x: (x.get("tna") or 0.0), reverse=True)[:5]:
                hist = CuentasWalletRateHist(
                    entidad=acc["fondo"],
                    tipo="cuenta_remunerada",
                    tna=acc.get("tna", 0)
                )
                session.add(hist)
            
            session.commit()

    async def on_system_periodic_sync(self, **kwargs):
        """Handler para sincronización periódica desde el scheduler core"""
        # Para este plugin, verificamos si ya existe una entrada hoy en el historial
        # Si no existe, guardamos el snapshot diario.
        with Session(engine) as session:
            hoy = datetime.utcnow().date()
            existing = session.exec(
                select(CuentasWalletRateHist).where(
                    CuentasWalletRateHist.fecha >= datetime.combine(hoy, datetime.min.time())
                )
            ).first()
            
            if not existing:
                self.logger.info(f"[{self.nombre_tecnico}] Snapshot del día no encontrado. Guardando...")
                await self.save_rates_to_hist()
