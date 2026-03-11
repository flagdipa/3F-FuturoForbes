"""
Script para registrar el plugin CriptoYa Multi-País en el sistema 3F
Ejecutar: python scripts/register_criptoya_plugin.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlmodel import Session, select
from backend.core.database import engine
from backend.models import Plugin


def register_criptoya_plugin():
    """Registrar el plugin de CriptoYa Multi-País en la base de datos"""
    
    session = Session(engine)
    
    try:
        # Verificar si ya existe
        existing = session.exec(
            select(Plugin).where(Plugin.nombre_tecnico == "criptoya_multi")
        ).first()
        
        if existing:
            print(f"✅ Plugin 'criptoya_multi' ya está registrado (ID: {existing.id_plugin})")
            print(f"   Estado: {'Activo' if existing.activo else 'Inactivo'}")
            return existing
        
        # Configuración por defecto
        default_config = {
            "enabled": True,
            "paises": ["AR", "BR", "CL", "CO", "MX"],
            "coins": ["BTC", "ETH", "USDT", "USDC"],
            "volumen_default": 0.1,
            "update_interval_minutes": 5,
            "auto_update": True,
            "notificar_cambio_significativo": False,
            "umbral_cambio_porcentaje": 5.0
        }
        
        # Crear plugin
        new_plugin = Plugin(
            nombre_tecnico="criptoya_multi",
            nombre_display="CriptoYa Multi-País",
            descripcion="Obtiene cotizaciones de criptomonedas de múltiples exchanges en Latinoamérica (11 países soportados)",
            version="1.0.0",
            autor="3F Team",
            instalado=True,
            activo=False,  # Se activa manualmente después de configurar
            configuracion=default_config,
            hooks_suscritos="daily_summary,account_sync"
        )
        
        session.add(new_plugin)
        session.commit()
        session.refresh(new_plugin)
        
        print(f"✅ Plugin 'criptoya_multi' registrado exitosamente!")
        print(f"   ID: {new_plugin.id_plugin}")
        print(f"   Nombre: {new_plugin.nombre_display}")
        print(f"   Hooks: {new_plugin.hooks_suscritos}")
        print(f"\n📝 Próximos pasos:")
        print(f"   1. Instala dependencias: pip install -r backend/plugins/criptoya_multi/requirements.txt")
        print(f"   2. Activa el plugin con: POST /api/plugins/{new_plugin.id_plugin}/activar")
        print(f"   3. Configura los países y coins a monitorear")
        print(f"\n📊 El plugin creará automáticamente las siguientes tablas:")
        print(f"   - criptoya_config (Configuración por usuario)")
        print(f"   - criptoya_paises (Catálogo de países)")
        print(f"   - criptoya_exchanges (Exchanges por país)")
        print(f"   - criptoya_coins (Criptomonedas)")
        print(f"   - criptoya_rates (Cotizaciones históricas)")
        print(f"   - criptoya_fees (Comisiones de retiro)")
        print(f"   - criptoya_alertas (Alertas de precio)")
        print(f"   - criptoya_favoritos (Pares favoritos)")
        
        return new_plugin
        
    except Exception as e:
        print(f"❌ Error registrando plugin: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("🔧 Registrando plugin CriptoYa Multi-País...\n")
    register_criptoya_plugin()
