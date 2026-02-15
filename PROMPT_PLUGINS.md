# PROMPT: Implementación del Sistema de Plugins para 3F

## 📋 CONTEXTO

Estás desarrollando el sistema de plugins para **3F (Futuro Forbes)**, un sistema de gestión financiera personal construido con FastAPI y SQLModel. El sistema necesita una arquitectura de plugins modular que permita extender funcionalidades sin modificar el core.

## 🎯 OBJETIVO

Implementar un sistema completo de plugins con:
1. Sistema de hooks para eventos
2. PluginManager para gestión de plugins
3. API endpoints para administrar plugins
4. Mínimo 3 plugins de ejemplo funcionales

## 📁 ESTRUCTURA ACTUAL DEL PROYECTO

```
3F/
├── backend/
│   ├── api/
│   │   └── config/
│   │       └── router_plugins.py      # API básica de plugins
│   ├── core/                          # Servicios core
│   ├── models/
│   │   └── models_plugins.py          # Modelo Plugin
│   └── plugins/                       # [CREAR] Directorio de plugins
├── frontend/
│   └── templates/
│       └── plugins.html               # Interfaz de gestión
```

## 🔧 MODELO DE DATOS EXISTENTE

El modelo `Plugin` ya existe en `backend/models/models_plugins.py`:

```python
class Plugin(SQLModel, table=True):
    __tablename__ = "plugins"
    
    id_plugin: Optional[int] = Field(default=None, primary_key=True)
    nombre_tecnico: str = Field(unique=True, index=True)  # ej: "telegram_bot"
    nombre_display: str
    descripcion: Optional[str] = None
    version: str = "1.0.0"
    autor: str = "3F Core"
    instalado: bool = Field(default=False)
    activo: bool = Field(default=False)
    configuracion: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    hooks_suscritos: str = Field(default="")  # Comma-separated
    
    creado_el: datetime = Field(default_factory=datetime.utcnow)
    actualizado_el: datetime = Field(default_factory=datetime.utcnow)
```

## 🪝 HOCKS DISPONIBLES EN EL SISTEMA

Los siguientes hooks deben poder ser utilizados por los plugins:

| Hook | Descripción | Parámetros |
|------|-------------|------------|
| `transaction_created` | Nueva transacción | transaction, user |
| `transaction_updated` | Transacción actualizada | transaction, changes |
| `budget_alert` | Presupuesto excedido | budget, percentage |
| `goal_reached` | Meta alcanzada | goal, amount |
| `account_sync` | Sincronización cuenta | account, transactions |
| `vault_file_upload` | Archivo subido | file, metadata |
| `report_generate` | Generar reporte | report_type, filters |
| `data_export` | Exportar datos | format, data |
| `data_import` | Importar datos | source, data |
| `login_attempt` | Intento de login | user, ip, success |
| `daily_summary` | Resumen diario | user, summary |
| `audit_event` | Evento de auditoría | action, entity, details |

## ✅ REQUERIMIENTOS

### 1. PluginManager (backend/core/plugin_manager.py)

Crear la clase `PluginManager` con los siguientes métodos:

```python
class PluginManager:
    def __init__(self):
        # Inicializar hooks registry
        
    async def load_plugins(self, session: Session):
        """Cargar todos los plugins activos desde la BD"""
        
    def register_hook(self, hook_name: str, plugin_id: int, callback: Callable):
        """Registrar un callback para un hook"""
        
    async def call_hook(self, hook_name: str, **kwargs):
        """Ejecutar todos los callbacks de un hook"""
        # Solo ejecutar plugins activos
        # Manejar errores individualmente (no detener otros plugins)
        
    async def install_plugin(self, plugin_data: PluginCreate, session: Session):
        """Instalar un nuevo plugin"""
        
    async def activate_plugin(self, plugin_id: int, session: Session):
        """Activar un plugin y registrar sus hooks"""
        
    async def deactivate_plugin(self, plugin_id: int, session: Session):
        """Desactivar un plugin y remover sus hooks"""
        
    def get_plugin_instance(self, nombre_tecnico: str):
        """Obtener instancia de un plugin cargado"""
```

### 2. Clase Base Plugin (backend/plugins/base.py)

```python
class BasePlugin(ABC):
    """Clase base que todos los plugins deben heredar"""
    
    nombre_tecnico: str
    nombre_display: str
    version: str = "1.0.0"
    autor: str = ""
    descripcion: str = ""
    hooks: List[str] = []
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.nombre_tecnico)
    
    @abstractmethod
    async def initialize(self):
        """Inicializar el plugin"""
        pass
    
    @abstractmethod
    async def shutdown(self):
        """Cerrar el plugin"""
        pass
    
    async def on_hook(self, hook_name: str, **kwargs):
        """Manejar un hook específico"""
        handler = getattr(self, f"on_{hook_name}", None)
        if handler:
            await handler(**kwargs)
```

### 3. Integración con el Sistema

Modificar los siguientes archivos para disparar hooks:

#### backend/api/transactions/router.py
```python
# En create_transaction, después de guardar:
await plugin_manager.call_hook(
    "transaction_created",
    transaction=new_transaction,
    user=current_user
)
```

#### backend/api/budgets/router.py
```python
# Al detectar que se excedió el presupuesto:
await plugin_manager.call_hook(
    "budget_alert",
    budget=budget,
    percentage=percentage_used
)
```

#### backend/api/goals/router.py
```python
# Al alcanzar una meta:
await plugin_manager.call_hook(
    "goal_reached",
    goal=goal,
    amount=current_amount
)
```

#### backend/api/auth/router.py
```python
# En login:
await plugin_manager.call_hook(
    "login_attempt",
    user=user,
    ip=request.client.host,
    success=success
)
```

### 4. Plugins de Ejemplo a Implementar

#### Plugin 1: Telegram Bot (backend/plugins/telegram_bot/)

**Archivos:**
- `__init__.py`
- `plugin.py`
- `config.json` (schema de configuración)

**Funcionalidad:**
- Enviar notificaciones cuando se crea una transacción
- Enviar alertas de presupuesto excedido
- Enviar notificación cuando se alcanza una meta

**Configuración:**
```json
{
  "bot_token": "string",
  "chat_id": "string",
  "notifications": {
    "transaction_created": true,
    "budget_alert": true,
    "goal_reached": true,
    "daily_summary": false
  }
}
```

#### Plugin 2: Email SMTP (backend/plugins/email_smtp/)

**Funcionalidad:**
- Enviar emails de alertas de presupuesto
- Notificar login desde nueva IP
- Reportes semanales automáticos

**Configuración:**
```json
{
  "smtp_host": "string",
  "smtp_port": 587,
  "username": "string",
  "password": "string",
  "use_tls": true,
  "from_email": "noreply@3f.com"
}
```

#### Plugin 3: Dólar Hoy Argentina (backend/plugins/dolar_hoy/)

**Funcionalidad:**
- Actualizar tasas de cambio automáticamente
- Soportar: Blue, MEP, CCL, Cripto
- Hook: `daily_summary` para actualizar tasas

**Configuración:**
```json
{
  "sources": ["blue", "mep", "ccl", "cripto"],
  "update_frequency": "hourly",
  "api_source": "dolarapi.com"
}
```

### 5. API Endpoints Adicionales (backend/api/config/router_plugins.py)

Extender el router existente con:

```python
@router.post("/{plugin_id}/activar")
async def activar_plugin(plugin_id: int):
    """Activar plugin y cargarlo en memoria"""

@router.post("/{plugin_id}/desactivar")
async def desactivar_plugin(plugin_id: int):
    """Desactivar plugin y descargarlo de memoria"""

@router.get("/{plugin_id}/config")
async def obtener_config(plugin_id: int):
    """Obtener configuración actual"""

@router.put("/{plugin_id}/config")
async def actualizar_config(plugin_id: int, config: dict):
    """Actualizar configuración JSON"""

@router.get("/{plugin_id}/logs")
async def obtener_logs(plugin_id: int):
    """Obtener logs del plugin"""
```

### 6. Frontend - Página de Plugins

Actualizar `frontend/templates/plugins.html` para incluir:

- **Lista de plugins:** Tabla con nombre, estado, versión, autor
- **Activar/Desactivar:** Toggle switches
- **Configuración:** Modal con formulario dinámico basado en schema JSON
- **Logs:** Visualización de logs por plugin
- **Instalar:** Botón para registrar nuevo plugin

## 🎨 FORMATO DE PLUGIN

Cada plugin debe estar en su propio directorio:

```
backend/plugins/
├── __init__.py
├── base.py                    # Clase base
├── manager.py                 # PluginManager
├── telegram_bot/
│   ├── __init__.py
│   ├── plugin.py              # Clase del plugin
│   ├── requirements.txt       # Dependencias extras
│   └── README.md              # Documentación
├── email_smtp/
│   ├── __init__.py
│   ├── plugin.py
│   ├── requirements.txt
│   └── README.md
└── dolar_hoy/
    ├── __init__.py
    ├── plugin.py
    ├── requirements.txt
    └── README.md
```

## 📋 EJEMPLO DE IMPLEMENTACIÓN DE PLUGIN

```python
# backend/plugins/telegram_bot/plugin.py
from backend.plugins.base import BasePlugin
import aiohttp

class TelegramBotPlugin(BasePlugin):
    nombre_tecnico = "telegram_bot"
    nombre_display = "Bot de Telegram"
    version = "1.0.0"
    autor = "3F Team"
    descripcion = "Envía notificaciones por Telegram"
    hooks = ["transaction_created", "budget_alert", "goal_reached"]
    
    async def initialize(self):
        self.logger.info(f"Inicializando {self.nombre_display}")
        # Validar config
        if not self.config.get("bot_token"):
            raise ValueError("bot_token requerido")
    
    async def shutdown(self):
        self.logger.info(f"Apagando {self.nombre_display}")
    
    async def on_transaction_created(self, transaction, user):
        if not self.config.get("notifications", {}).get("transaction_created"):
            return
            
        message = f"💰 Nueva transacción: ${transaction.monto}"
        await self._send_message(message)
    
    async def on_budget_alert(self, budget, percentage):
        if not self.config.get("notifications", {}).get("budget_alert"):
            return
            
        message = f"⚠️ Presupuesto excedido: {percentage}%"
        await self._send_message(message)
    
    async def on_goal_reached(self, goal, amount):
        if not self.config.get("notifications", {}).get("goal_reached"):
            return
            
        message = f"🎉 Meta alcanzada: {goal.nombre_meta}"
        await self._send_message(message)
    
    async def _send_message(self, text: str):
        token = self.config["bot_token"]
        chat_id = self.config["chat_id"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        
        async with aiohttp.ClientSession() as session:
            await session.post(url, json={
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            })
```

## 🔒 CONSIDERACIONES DE SEGURIDAD

1. **Validación de configuración:** Validar schema JSON antes de guardar
2. **Aislamiento de errores:** Un plugin que falla no debe afectar otros
3. **Timeouts:** Establecer timeouts para hooks (ej: 30 segundos)
4. **Rate limiting:** Prevenir abuso de plugins en hooks
5. **Logs de auditoría:** Registrar activación/desactivación de plugins

## 🧪 TESTING

Crear tests para:

1. **PluginManager:**
   - `test_register_hook()`
   - `test_call_hook()`
   - `test_activate_plugin()`
   - `test_deactivate_plugin()`

2. **Plugins individuales:**
   - `test_telegram_bot_send_message()`
   - `test_email_smtp_send()`
   - `test_dolar_hoy_fetch_rates()`

3. **Integración:**
   - `test_hook_fires_on_transaction_create()`
   - `test_plugin_error_isolation()`

## 📚 DOCUMENTACIÓN A GENERAR

1. **README.md** en `backend/plugins/` - Guía para desarrollar plugins
2. **API.md** - Documentación de endpoints
3. **HOOKS.md** - Lista de hooks disponibles
4. **EJEMPLOS.md** - Ejemplos de plugins comunes

## ✨ CRITERIOS DE ACEPTACIÓN

- [ ] PluginManager implementado y funcional
- [ ] Clase BasePlugin abstracta creada
- [ ] 3 plugins de ejemplo funcionando (Telegram, Email, Dólar)
- [ ] Hooks disparando correctamente en transacciones, presupuestos, metas
- [ ] API endpoints para gestionar plugins
- [ ] Interfaz web para activar/desactivar/configurar plugins
- [ ] Tests unitarios con cobertura > 80%
- [ ] Documentación completa
- [ ] Manejo de errores robusto
- [ ] Plugins aislados (fallo de uno no afecta al sistema)

## 🚀 PRIORIDAD

**ALTA** - Esta funcionalidad es crítica para la extensibilidad del sistema y permitirá a los usuarios personalizar 3F sin modificar código core.

## 📝 NOTAS ADICIONALES

- Usar `asyncio` para operaciones asíncronas
- Los plugins pueden requerir librerías externas (manejar en requirements.txt)
- Considerar hot-reloading de plugins en desarrollo
- Implementar sistema de logs por plugin
- Crear interfaz de marketplace para plugins futuros

---

**Fecha:** 14 de Febrero 2026
**Sistema:** 3F (Futuro Forbes) v1.0.0
**Arquitectura:** FastAPI + SQLModel + AsyncIO
