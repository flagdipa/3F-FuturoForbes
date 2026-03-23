# Spec: Sistema de Plugins

## Goal
Definir la arquitectura extensible del sistema 3F mediante plugins ("Sistema de Plugins"), permitiendo expandir la funcionalidad sin modificar el código core del sistema. Además, documentar los plugins estándar o básicos que se apoyan en esta arquitectura genérica.

## Capabilities

Esta especificación cubre la capa de integraciones modulares del backend:

1. **Gestión de Ciclo de Vida de Plugins:**
   - Carga dinámica desde la base de datos (modelo `Plugin`).
   - Hooks de activación (`activate_plugin`) y desactivación (`deactivate_plugin`) en memoria usando un `PluginManager` central.
   - Aislamiento de fallos (Un plugin erróneo no tumba el core del sistema).

2. **Extensibilidad Basada en Eventos (Hooks):**
   - El sistema principal (routers de transacciones, auth, presupuestos) dispara eventos ("Hooks").
   - Los plugins se subscriben asíncronamente a los eventos mediante la herencia de la clase `BasePlugin`.

3. **Plugins Simples (Standard Integrations):**
   - **Telegram Bot:**
     - Envía notificaciones Push por Telegram ante transacciones nuevas, excesos en presupuestos o metas cumplidas.
   - **Email SMTP:**
     - Maneja el envío de reportes semanales, notificaciones críticas de sistema y logs de login.
   - **Dólar Hoy (Argentina):**
     - Sincronizador horario de tasas de cambio local (Mep, CCL, Blue, Cripto).

## Data Models

Toda la persistencia y estado de los plugins giran sobre el modelo principal `Plugin` en `backend/models/models_plugins.py`:

```python
class Plugin(SQLModel, table=True):
    id_plugin: Optional[int] = Field(default=None, primary_key=True)
    nombre_tecnico: str = Field(unique=True, index=True) # e.g., "telegram_bot"
    nombre_display: str
    descripcion: Optional[str] = None
    version: str = "1.0.0"
    autor: str = "3F Core"
    instalado: bool = Field(default=False)
    activo: bool = Field(default=False)
    configuracion: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    hooks_suscritos: str = Field(default="") # comma-separated
    creado_el: datetime
    actualizado_el: datetime
```

### Arquitectura en Memoria
- La clase abstracta **`BasePlugin`** (en `backend/plugins/base.py`) exige los métodos: `initialize()`, `shutdown()`, y `on_hook()`.
- El **`PluginManager`** (en `backend/core/plugin_manager.py`) maneja un registry interno de *hooks* (`register_hook`) y despacha la ejecución (`call_hook`).

## API Endpoints

Interfaces para la administración de plugins expuestas en `/api/v1/plugins`:

- `GET /` - Listar estado de todos los plugins.
- `POST /install` - Registrar/instalar un nuevo plugin en la BD.
- `POST /{id}/activate` - Activar y cargar en memoria un plugin instalado.
- `POST /{id}/deactivate` - Descargar memoria y desactivar plugin.
- `DELETE /{id}` - Desinstalar.
- `GET /{id}/config` - Leer JSON de configuración almacenado.
- `PUT /{id}/config` - Escribir y persistir nuevo JSON.
- `GET /{id}/logs` - Recuperar trazas y auditoría aislada del plugin.

## Hooks del Sistema Core (Registry)

De acuerdo al `PROMPT_PLUGINS.md`, el pool de hooks soportados es:
- Transaccionales: `transaction_created`, `transaction_updated`
- Presupuestales y Metas: `budget_alert`, `goal_reached`
- Sistema y Sesión: `account_sync`, `vault_file_upload`, `report_generate`, `login_attempt`, `audit_event`
- Data Hooks: `data_export`, `data_import`, `daily_summary`

## Scenarios

- **Scenario: Telegram Notifica Creación de Transacción**
  - *Given* el plugin `telegram_bot` está "activo" en BD y cargado en el `PluginManager`, con un `chat_id` configurado y la flag `"transaction_created": true`.
  - *When* el router de fastapi despacha un HTTP 201 en `/transactions` llamando de forma no-bloqueante a `await plugin_manager.call_hook("transaction_created")`.
  - *Then* el `PluginManager` despacha la llamada, y el objeto instanciado de `TelegramBotPlugin` ejecuta su método `on_transaction_created` emitiendo un mensaje al API de Telegram.

- **Scenario: Falla de un Plugin Aislado**
  - *Given* que `email_smtp` se queda sin conexión con el host SMTP configurado.
  - *When* se intenta enviar un reporte mediante `call_hook("budget_alert")`.
  - *Then* el método `on_budget_alert` interior arroja un timeout, pero el `PluginManager` atrapa el `Exception`, logueando localmente el error del módulo y permitiendo que la respuesta HTTP siga fluyendo a quien originó la petición original (por ejemplo, el Frontend) sin tumbar el server Uvicorn/FastAPI.
