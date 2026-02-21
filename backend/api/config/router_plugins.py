"""
Extended Plugin Router - API endpoints para gestión de plugins
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Dict, Any
from datetime import datetime

from backend.core.database import get_session
from backend.core.plugin_manager import plugin_manager
from backend.models.models_plugins import Plugin
from backend.api.auth.deps import get_current_user
from backend.api.config.schemas_plugins import PluginRead, PluginCreate, PluginUpdate

router = APIRouter(
    prefix="/plugins", 
    tags=["Plugins"], 
    dependencies=[Depends(get_current_user)]
)


@router.get("/", response_model=List[PluginRead])
def listar_plugins(session: Session = Depends(get_session)):
    """
    Listar todos los plugins instalados en el sistema.
    Incluye plugins activos e inactivos.
    """
    plugins = session.exec(select(Plugin)).all()
    return plugins


@router.get("/activos")
def listar_plugins_activos():
    """
    Listar plugins actualmente cargados en memoria.
    """
    return {
        "plugins_cargados": plugin_manager.get_loaded_plugins(),
        "total": len(plugin_manager.get_loaded_plugins())
    }


@router.post("/", response_model=PluginRead, status_code=status.HTTP_201_CREATED)
async def instalar_plugin(
    plugin_in: PluginCreate, 
    session: Session = Depends(get_session)
):
    """
    Instalar un nuevo plugin en el sistema.
    Registra el plugin en la base de datos pero no lo activa automáticamente.
    """
    try:
        new_plugin = await plugin_manager.install_plugin(
            plugin_data=plugin_in.dict(),
            session=session
        )
        return new_plugin
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error instalando plugin: {str(e)}")


@router.get("/{plugin_id}", response_model=PluginRead)
def obtener_plugin(plugin_id: int, session: Session = Depends(get_session)):
    """
    Obtener información detallada de un plugin específico.
    """
    plugin = session.get(Plugin, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin no encontrado")
    return plugin


@router.patch("/{plugin_id}", response_model=PluginRead)
def actualizar_plugin(
    plugin_id: int, 
    plugin_in: PluginUpdate, 
    session: Session = Depends(get_session)
):
    """
    Actualizar información de un plugin (nombre, descripción, versión, etc).
    No activa/desactiva el plugin, solo actualiza metadatos.
    """
    db_plugin = session.get(Plugin, plugin_id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="Plugin no encontrado")
    
    # Actualizar campos
    plugin_data = plugin_in.dict(exclude_unset=True)
    for key, value in plugin_data.items():
        # No permitir cambiar activo aquí, usar endpoint específico
        if key == "activo":
            continue
        setattr(db_plugin, key, value)
    
    db_plugin.actualizado_el = datetime.utcnow()
    session.add(db_plugin)
    session.commit()
    session.refresh(db_plugin)
    
    return db_plugin


@router.post("/{plugin_id}/activar")
async def activar_plugin(
    plugin_id: int, 
    session: Session = Depends(get_session)
):
    """
    Activar un plugin y cargarlo en memoria.
    El plugin comenzará a responder a sus hooks suscritos.
    """
    try:
        await plugin_manager.activate_plugin(plugin_id, session)
        return {
            "success": True,
            "message": "Plugin activado correctamente",
            "plugin_id": plugin_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error activando plugin: {str(e)}")


@router.post("/{plugin_id}/desactivar")
async def desactivar_plugin(
    plugin_id: int, 
    session: Session = Depends(get_session)
):
    """
    Desactivar un plugin y descargarlo de memoria.
    El plugin dejará de responder a hooks.
    """
    try:
        await plugin_manager.deactivate_plugin(plugin_id, session)
        return {
            "success": True,
            "message": "Plugin desactivado correctamente",
            "plugin_id": plugin_id
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error desactivando plugin: {str(e)}")


@router.get("/{plugin_id}/config")
def obtener_configuracion_plugin(
    plugin_id: int, 
    session: Session = Depends(get_session)
):
    """
    Obtener la configuración actual de un plugin.
    """
    plugin = session.get(Plugin, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin no encontrado")
    
    return {
        "plugin_id": plugin_id,
        "nombre_tecnico": plugin.nombre_tecnico,
        "configuracion": plugin.configuracion,
        "schema": _get_plugin_config_schema(plugin.nombre_tecnico)
    }


@router.put("/{plugin_id}/config")
async def actualizar_configuracion_plugin(
    plugin_id: int, 
    config: Dict[str, Any],
    session: Session = Depends(get_session)
):
    """
    Actualizar la configuración de un plugin.
    Si el plugin está activo, se recarga con la nueva configuración.
    """
    plugin = session.get(Plugin, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin no encontrado")
    
    # Actualizar configuración
    plugin.configuracion = config
    plugin.actualizado_el = datetime.utcnow()
    session.add(plugin)
    session.commit()
    session.refresh(plugin)
    
    # Si el plugin está activo, recargarlo
    if plugin.activo and plugin_manager.is_plugin_loaded(plugin.nombre_tecnico):
        # Desactivar y reactivar para aplicar nueva configuración
        await plugin_manager.deactivate_plugin(plugin_id, session)
        await plugin_manager.activate_plugin(plugin_id, session)
    
    return {
        "success": True,
        "message": "Configuración actualizada",
        "plugin_id": plugin_id,
        "configuracion": plugin.configuracion
    }


@router.get("/{plugin_id}/estado")
def obtener_estado_plugin(plugin_id: int, session: Session = Depends(get_session)):
    """
    Obtener el estado actual de un plugin (BD y memoria).
    """
    plugin = session.get(Plugin, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin no encontrado")
    
    return {
        "plugin_id": plugin_id,
        "nombre_tecnico": plugin.nombre_tecnico,
        "en_base_de_datos": {
            "instalado": plugin.instalado,
            "activo": plugin.activo
        },
        "en_memoria": {
            "cargado": plugin_manager.is_plugin_loaded(plugin.nombre_tecnico),
            "hooks_registrados": len(plugin_manager.get_hook_subscribers(plugin.nombre_tecnico))
        }
    }


@router.post("/{plugin_id}/test")
async def probar_plugin(
    plugin_id: int, 
    session: Session = Depends(get_session)
):
    """
    Probar un plugin activo disparando sus hooks de prueba.
    """
    plugin = session.get(Plugin, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin no encontrado")
    
    if not plugin_manager.is_plugin_loaded(plugin.nombre_tecnico):
        raise HTTPException(
            status_code=400, 
            detail="El plugin no está activo. Actívalo primero."
        )
    
    try:
        # Disparar hooks de prueba
        test_results = []
        for hook in plugin.hooks_suscritos.split(","):
            hook = hook.strip()
            if hook:
                await plugin_manager.call_hook(hook, test_mode=True)
                test_results.append({"hook": hook, "status": "ok"})
        
        return {
            "success": True,
            "message": "Plugin probado correctamente",
            "plugin": plugin.nombre_tecnico,
            "tests": test_results
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error probando plugin: {str(e)}"
        )


@router.get("/hooks/disponibles")
def listar_hooks_disponibles():
    """
    Listar todos los hooks disponibles en el sistema.
    """
    return {
        "hooks": [
            {"nombre": "transaction_created", "descripcion": "Nueva transacción creada"},
            {"nombre": "transaction_updated", "descripcion": "Transacción actualizada"},
            {"nombre": "budget_alert", "descripcion": "Presupuesto excedido"},
            {"nombre": "goal_reached", "descripcion": "Meta alcanzada"},
            {"nombre": "account_sync", "descripcion": "Sincronización de cuenta"},
            {"nombre": "vault_file_upload", "descripcion": "Archivo subido a vault"},
            {"nombre": "report_generate", "descripcion": "Generación de reporte"},
            {"nombre": "data_export", "descripcion": "Exportación de datos"},
            {"nombre": "data_import", "descripcion": "Importación de datos"},
            {"nombre": "login_attempt", "descripcion": "Intento de login"},
            {"nombre": "daily_summary", "descripcion": "Resumen diario"},
            {"nombre": "audit_event", "descripcion": "Evento de auditoría"}
        ]
    }


@router.delete("/{plugin_id}", status_code=status.HTTP_204_NO_CONTENT)
async def desinstalar_plugin(
    plugin_id: int, 
    session: Session = Depends(get_session)
):
    """
    Desinstalar un plugin del sistema.
    Si está activo, primero lo desactiva.
    """
    plugin = session.get(Plugin, plugin_id)
    if not plugin:
        raise HTTPException(status_code=404, detail="Plugin no encontrado")
    
    # Desactivar si está activo
    if plugin.activo:
        try:
            await plugin_manager.deactivate_plugin(plugin_id, session)
        except Exception as e:
            logger.error(f"Error desactivando plugin antes de desinstalar: {e}")
    
    # Eliminar de la base de datos
    session.delete(plugin)
    session.commit()
    
    return None


def _get_plugin_config_schema(nombre_tecnico: str) -> Dict[str, Any]:
    """
    Obtener el schema de configuración esperado para un plugin.
    Esto es útil para el frontend saber qué campos mostrar.
    """
    schemas = {
        "telegram_bot": {
            "bot_token": {"type": "string", "required": True, "label": "Token del Bot"},
            "chat_id": {"type": "string", "required": True, "label": "Chat ID"},
            "notifications": {
                "type": "object",
                "properties": {
                    "transaction_created": {"type": "boolean", "label": "Nueva transacción"},
                    "budget_alert": {"type": "boolean", "label": "Alerta de presupuesto"},
                    "goal_reached": {"type": "boolean", "label": "Meta alcanzada"},
                    "daily_summary": {"type": "boolean", "label": "Resumen diario"}
                }
            }
        },
        "email_smtp": {
            "smtp_host": {"type": "string", "required": True, "label": "Servidor SMTP"},
            "smtp_port": {"type": "integer", "required": True, "label": "Puerto", "default": 587},
            "username": {"type": "string", "required": True, "label": "Usuario"},
            "password": {"type": "string", "required": True, "label": "Contraseña", "secret": True},
            "use_tls": {"type": "boolean", "label": "Usar TLS", "default": True},
            "from_email": {"type": "string", "label": "Email remitente"},
            "notifications": {
                "type": "object",
                "properties": {
                    "transaction_created": {"type": "boolean"},
                    "budget_alert": {"type": "boolean"},
                    "goal_reached": {"type": "boolean"},
                    "login_attempt": {"type": "boolean"}
                }
            }
        },
        "dolar_hoy": {
            "sources": {
                "type": "array",
                "items": {"type": "string", "enum": ["blue", "mep", "ccl", "cripto"]},
                "label": "Fuentes",
                "default": ["blue", "mep", "ccl"]
            },
            "update_frequency": {"type": "string", "enum": ["hourly", "daily"], "default": "hourly"},
            "create_divisas_if_missing": {"type": "boolean", "label": "Crear divisas automáticamente", "default": True}
        },
        "argentina_datos": {
            "intervalo_actualizacion_minutos": {"type": "integer", "label": "Intervalo Sincronización (min)", "default": 60},
            "apis_disponibles": {
                "type": "object",
                "label": "Fuentes de Datos",
                "properties": {
                    "cotizaciones_actuales": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Cotizaciones actuales", "default": True}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones"}, "label": {"type": "string", "hidden": True, "default": "Cotizaciones actuales"}}},
                    "dolar_blue": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Dólar Blue", "default": True}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones/dolares/blue"}, "label": {"type": "string", "hidden": True, "default": "Dólar Blue"}}},
                    "dolar_oficial": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Dólar Oficial", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones/dolares/oficial"}, "label": {"type": "string", "hidden": True, "default": "Dólar Oficial"}}},
                    "dolar_bolsa": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Dólar Bolsa / MEP", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones/dolares/bolsa"}, "label": {"type": "string", "hidden": True, "default": "Dólar Bolsa / MEP"}}},
                    "dolar_ccl": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Dólar CCL", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones/dolares/contadoconliqui"}, "label": {"type": "string", "hidden": True, "default": "Dólar CCL"}}},
                    "dolar_cripto": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Dólar Cripto", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones/dolares/cripto"}, "label": {"type": "string", "hidden": True, "default": "Dólar Cripto"}}},
                    "dolar_mayorista": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Dólar Mayorista", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones/dolares/mayorista"}, "label": {"type": "string", "hidden": True, "default": "Dólar Mayorista"}}},
                    "dolar_tarjeta": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Dólar Tarjeta", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones/dolares/tarjeta"}, "label": {"type": "string", "hidden": True, "default": "Dólar Tarjeta"}}},
                    "euro": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Euro", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones/eur"}, "label": {"type": "string", "hidden": True, "default": "Euro"}}},
                    "real": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Real Brasileño", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/cotizaciones/brl"}, "label": {"type": "string", "hidden": True, "default": "Real Brasileño"}}},
                    "inflacion": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Inflación mensual", "default": True}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/inflacion"}, "label": {"type": "string", "hidden": True, "default": "Inflación mensual"}}},
                    "plazo_fijo": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Tasas de Plazo Fijo", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/tasas/plazoFijo"}, "label": {"type": "string", "hidden": True, "default": "Tasas de Plazo Fijo"}}},
                    "plazos_fijos_entidades": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Tasas por entidad", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/tasas/plazosFijos"}, "label": {"type": "string", "hidden": True, "default": "Tasas por entidad"}}},
                    "depositos_30_dias": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Depósitos a 30 días", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/tasas/depositos30Dias"}, "label": {"type": "string", "hidden": True, "default": "Depósitos a 30 días"}}},
                    "indice_uva": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Índice UVA", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/indices/uva"}, "label": {"type": "string", "hidden": True, "default": "Índice UVA"}}},
                    "fci": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Fondos Comunes", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/fci"}, "label": {"type": "string", "hidden": True, "default": "Fondos Comunes"}}},
                    "riesgo_pais": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Riesgo País", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/indices/riesgo-pais/ultimo"}, "label": {"type": "string", "hidden": True, "default": "Riesgo País"}}},
                    "criptopesos": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Criptopesos", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/criptopesos"}, "label": {"type": "string", "hidden": True, "default": "Criptopesos"}}},
                    "cuentas_remuneradas_usd": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Cuentas Remun. USD", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/cuentas-remuneradas-usd"}, "label": {"type": "string", "hidden": True, "default": "Cuentas Remun. USD"}}},
                    "hipotecarios_uva": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Hipotecarios UVA", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/hipotecarios-uva"}, "label": {"type": "string", "hidden": True, "default": "Hipotecarios UVA"}}},
                    "creditos_hipotecarios": {"type": "object", "properties": {"activa": {"type": "boolean", "label": "Créditos Hipotecarios", "default": False}, "endpoint": {"type": "string", "hidden": True, "default": "/v1/finanzas/creditos"}, "label": {"type": "string", "hidden": True, "default": "Créditos Hipotecarios"}}}
                }
            }
        },
        "cuentas_wallet": {
            "update_interval": {"type": "integer", "label": "Intervalo (min)", "default": 1440},
            "compare_options": {
                "type": "object",
                "label": "Opciones Comparación",
                "properties": {
                    "fixed_terms": {"type": "boolean", "label": "Plazos Fijos", "default": True},
                    "wallets": {"type": "boolean", "label": "Billeteras", "default": True}
                }
            }
        }
    }
    
    return schemas.get(nombre_tecnico, {})

# --- Endpoints específicos para Argentina Datos ---

@router.post("/argentina_datos/actualizar")
async def actualizar_argentina_datos():
    """Fuerza actualización manual de todas las APIs activas del plugin"""
    plugin = plugin_manager.get_plugin_instance("argentina_datos")
    if not plugin:
        raise HTTPException(404, "Plugin 'argentina_datos' no está activo")
    
    count = await plugin.sync_enabled_apis()
    return {"status": "ok", "mensaje": f"Sincronizadas {count} APIs"}

@router.get("/argentina_datos/datos")
async def obtener_datos_argentina():
    """Retorna los datos cacheados de todas las APIs activas"""
    plugin = plugin_manager.get_plugin_instance("argentina_datos")
    if not plugin:
        raise HTTPException(404, "Plugin 'argentina_datos' no está activo")
    
    return await plugin.get_active_data()


# Importar logger
import logging
logger = logging.getLogger(__name__)
