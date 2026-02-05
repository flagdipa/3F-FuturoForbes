from sqlmodel import Session, select
from ..models.models import ListaCuentas, LibroTransacciones
from ..models.models_advanced import Activo, Inversion
from ..models.models_wealth import WealthSnapshot
from decimal import Decimal
from datetime import datetime

from ..core.fx_service import fx_service

class WealthService:
    @staticmethod
    async def calculate_total_wealth(session: Session, user_id: int, target_currency: str = "ARS"):
        """
        Calculates a breakdown of the user's total wealth revalued in target_currency.
        """
        rates = await fx_service.get_rates()
        
        # 1. Accounts
        cuentas = session.exec(select(ListaCuentas)).all()
        # Sumar saldos revaluados
        total_liquido = Decimal("0.00")
        for c in cuentas:
            # We need the currency code for each account. 
            # Simplified: assuming accounts have a relationship with Divisa
            # For now, we'll try to find the ISO code.
            try:
                from ..models.models import Divisa
                divisa = session.get(Divisa, c.id_divisa)
                iso = divisa.codigo_iso if divisa else "ARS"
            except:
                iso = "ARS"
            
            amount_revalued = fx_service.convert(c.saldo_inicial, iso, target_currency, rates)
            total_liquido += amount_revalued
        
        # 2. Assets (Assuming ARS default for physical assets unless specified)
        try:
            activos = session.exec(select(Activo).where(Activo.activo == 1)).all()
            total_activos = sum(fx_service.convert(Decimal(str(a.valor_actual)), "ARS", target_currency, rates) for a in activos)
        except:
            total_activos = Decimal("0.00")
            
        # 3. Investments (Usually in USD or ARS)
        try:
            inversiones = session.exec(select(Inversion).where(Inversion.activo == 1)).all()
            total_inversiones = Decimal("0.00")
            for inv in inversiones:
                # Assuming crypto is in its own symbol (BTC, ETH) in rates
                curr = inv.simbolo if inv.simbolo in rates else "USD_BLUE"
                value_original = Decimal(str(inv.cantidad)) * Decimal(str(inv.precio_actual))
                total_inversiones += fx_service.convert(value_original, curr, target_currency, rates)
        except:
            total_inversiones = Decimal("0.00")

        return {
            "total_liquido": total_liquido,
            "total_activos": total_activos,
            "total_inversiones": total_inversiones,
            "patrimonio_neto": total_liquido + total_activos + total_inversiones,
            "target_currency": target_currency,
            "rates": rates
        }

    @staticmethod
    async def capture_snapshot(session: Session, user_id: int):
        """
        Calculates and persists a wealth snapshot (always in ARS base for history).
        """
        breakdown = await WealthService.calculate_total_wealth(session, user_id, "ARS")
        
        snapshot = WealthSnapshot(
            fecha=datetime.utcnow(),
            total_liquido=breakdown["total_liquido"],
            total_activos=breakdown["total_activos"],
            total_inversiones=breakdown["total_inversiones"],
            patrimonio_neto=breakdown["patrimonio_neto"],
            id_usuario=user_id
        )
        
        session.add(snapshot)
        session.commit()
        return snapshot

wealth_service = WealthService()
