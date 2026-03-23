from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from ...dependencies import get_db
from ...models.models_v2 import Plugin, User
from ..auth.deps import get_current_user
from ...core.plugin_manager import plugin_manager
from ...core.hooks_engine import get_registered_hooks

router = APIRouter()

@router.get("/activos", summary="Plugins activos en memoria")
def list_active_plugins(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns names of currently loaded (active) plugins for the sidebar."""
    plugin_manager.db = db
    loaded = list(plugin_manager.loaded_plugins.keys()) if hasattr(plugin_manager, 'loaded_plugins') else []
    return {"plugins_cargados": loaded}


@router.get("/", response_model=List[Plugin])
def list_plugins(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # discover_plugins returns manifest info mixed with DB state
    # But for simplicity, we return the DB records for installed plugins
    # and maybe we should merge them with non-installed ones?
    # Actually, the frontend needs to know which ones are NOT installed too.
    
    # Update DB with current discovery if needed? No, let's keep it simple.
    # The discover_plugins method in plugin_manager returns List[Dict]
    plugin_manager.db = db
    discovered = plugin_manager.discover_plugins()
    
    # We want to return a list of Plugin objects (or dicts that look like them)
    # Since discovered is List[Dict], and some might not be in DB yet, 
    # we can't just return DB records.
    return discovered

@router.post("/", response_model=Plugin)
def install_plugin(data: Dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tech_name = data.get("technical_name") or data.get("nombre_tecnico")
    if not tech_name:
        raise HTTPException(status_code=400, detail="technical_name is required")
        
    plugin_manager.db = db
    if plugin_manager.install_plugin(tech_name):
        db_plugin = db.exec(select(Plugin).where(Plugin.technical_name == tech_name)).first()
        return db_plugin
    raise HTTPException(status_code=500, detail=f"Failed to install plugin {tech_name}")

@router.delete("/{id}")
def uninstall_plugin(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_plugin = db.get(Plugin, id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
        
    plugin_manager.db = db
    if plugin_manager.uninstall_plugin(db_plugin.technical_name):
        return {"status": "success", "message": "Plugin uninstalled"}
    raise HTTPException(status_code=500, detail="Failed to uninstall plugin")

@router.post("/{id}/activar")
def activate_plugin(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_plugin = db.get(Plugin, id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
        
    plugin_manager.db = db
    if plugin_manager.activate_plugin(db_plugin.technical_name):
        return {"status": "success", "is_active": True}
    raise HTTPException(status_code=500, detail="Failed to activate plugin")

@router.post("/{id}/desactivar")
def deactivate_plugin(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_plugin = db.get(Plugin, id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
        
    plugin_manager.db = db
    if plugin_manager.deactivate_plugin(db_plugin.technical_name):
        return {"status": "success", "is_active": False}
    raise HTTPException(status_code=500, detail="Failed to deactivate plugin")

@router.put("/{id}/config")
def update_plugin_config(id: int, config: Dict[str, Any], db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_plugin = db.get(Plugin, id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
        
    plugin_manager.db = db
    if plugin_manager.set_plugin_config(db_plugin.technical_name, config):
        db.refresh(db_plugin)
        return db_plugin
    raise HTTPException(status_code=500, detail="Failed to update config")

@router.get("/{id}/estado")
def get_plugin_status(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_plugin = db.get(Plugin, id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
        
    instance = plugin_manager.loaded_plugins.get(db_plugin.technical_name)
    
    return {
        "technical_name": db_plugin.technical_name,
        "en_base_de_datos": {
            "instalado": True,
            "activo": db_plugin.is_active
        },
        "en_memoria": {
            "cargado": instance is not None,
            "hooks_registrados": len([h for h in get_registered_hooks().values() if any(cb.__module__.startswith(f"backend.plugins.{db_plugin.technical_name}") for cb in h)])
        }
    }

@router.get("/hooks/disponibles")
def list_available_hooks():
    # Hardcoded list of hooks supported by the system
    return {
        "hooks": [
            {"nombre": "login_attempt", "descripcion": "Se dispara al intentar iniciar sesión"},
            {"nombre": "transaction_created", "descripcion": "Se dispara después de crear una transacción"},
            {"nombre": "db_sync", "descripcion": "Se dispara durante la sincronización periódica"},
            {"nombre": "forecasting_generated", "descripcion": "Se dispara al generar proyecciones"},
            {"nombre": "export_data", "descripcion": "Se dispara al exportar información"}
        ]
    }

@router.post("/{id}/test")
def test_plugin(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_plugin = db.get(Plugin, id)
    if not db_plugin:
        raise HTTPException(status_code=404, detail="Plugin not found")
    
    # Mock test: trigger some common hooks
    return {
        "status": "success",
        "tests": ["test_hook_1", "test_hook_2"]
    }
