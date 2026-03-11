"""
Script para registrar el plugin Backup Automático en el sistema 3F
Ejecutar: python scripts/register_backup_plugin.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlmodel import Session, select
from backend.core.database import engine
from backend.models import Plugin


def register_backup_plugin():
    """Registrar el plugin de backup automático en la base de datos"""
    
    session = Session(engine)
    
    try:
        # Verificar si ya existe
        existing = session.exec(
            select(Plugin).where(Plugin.nombre_tecnico == "backup_automatico")
        ).first()
        
        if existing:
            print(f"✅ Plugin 'backup_automatico' ya está registrado (ID: {existing.id_plugin})")
            print(f"   Estado: {'Activo' if existing.activo else 'Inactivo'}")
            return existing
        
        # Configuración por defecto
        default_config = {
            "enabled": True,
            "frequency": "daily",
            "backup_time": "02:00",
            "retention_days": 30,
            "compression": True,
            "local_path": "backups/",
            "s3": {
                "enabled": False,
                "bucket": "",
                "access_key": "",
                "secret_key": "",
                "region": "us-east-1",
                "prefix": "3f-backups/"
            },
            "notifications": {
                "on_success": False,
                "on_failure": True
            }
        }
        
        # Crear plugin
        new_plugin = Plugin(
            nombre_tecnico="backup_automatico",
            nombre_display="Backup Automático",
            descripcion="Crea backups automáticos de la base de datos MySQL y los almacena localmente o en AWS S3",
            version="1.0.0",
            autor="3F Team",
            instalado=True,
            activo=False,  # Se activa manualmente después de configurar
            configuracion=default_config,
            hooks_suscritos="daily_summary,audit_event"
        )
        
        session.add(new_plugin)
        session.commit()
        session.refresh(new_plugin)
        
        print(f"✅ Plugin 'backup_automatico' registrado exitosamente!")
        print(f"   ID: {new_plugin.id_plugin}")
        print(f"   Nombre: {new_plugin.nombre_display}")
        print(f"   Hooks: {new_plugin.hooks_suscritos}")
        print(f"\n📝 Próximos pasos:")
        print(f"   1. Configura el plugin vía API o interfaz web")
        print(f"   2. Activa el plugin con: POST /api/plugins/{new_plugin.id_plugin}/activar")
        print(f"   3. Instala dependencias: pip install -r backend/plugins/backup_automatico/requirements.txt")
        
        return new_plugin
        
    except Exception as e:
        print(f"❌ Error registrando plugin: {e}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("🔧 Registrando plugin Backup Automático...\n")
    register_backup_plugin()
