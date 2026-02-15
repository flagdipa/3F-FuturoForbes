# Sistema de Plugins - 3F (Futuro Forbes)

Sistema modular extensible para 3F que permite agregar funcionalidades sin modificar el código core.

## 🎯 Características

- ✅ Arquitectura modular tipo PrestaShop
- ✅ Sistema de hooks para eventos
- ✅ Activación/desactivación en runtime
- ✅ Configuración JSON flexible
- ✅ Aislamiento de errores
- ✅ 3 plugins incluidos (Telegram, Email, Dólar)

## 📁 Estructura

```
backend/plugins/
├── __init__.py              # Package init
├── base.py                  # Clase BasePlugin
├── telegram_bot/            # Plugin Telegram
│   ├── __init__.py
│   ├── plugin.py
│   └── requirements.txt
├── email_smtp/              # Plugin Email
│   ├── __init__.py
│   ├── plugin.py
│   └── requirements.txt
└── dolar_hoy/               # Plugin Dólar
    ├── __init__.py
    ├── plugin.py
    └── requirements.txt
```

## 🚀 Plugins Incluidos

### 1. Telegram Bot (`telegram_bot`)

**Descripción:** Envía notificaciones por Telegram

**Hooks:**
- `transaction_created` - Nueva transacción
- `budget_alert` - Alerta de presupuesto
- `goal_reached` - Meta alcanzada
- `daily_summary` - Resumen diario

**Configuración:**
```json
{
  "bot_token": "123456:ABC-DEF1234...",
  "chat_id": "-1001234567890",
  "notifications": {
    "transaction_created": true,
    "budget_alert": true,
    "goal_reached": true,
    "daily_summary": false
  }
}
```

**Instalación:**
1. Crear bot con @BotFather
2. Obtener token
3. Obtener chat_id
4. Configurar en el plugin

---

### 2. Email SMTP (`email_smtp`)

**Descripción:** Envía notificaciones por email

**Hooks:**
- `transaction_created`
- `budget_alert`
- `goal_reached`
- `login_attempt`

**Configuración:**
```json
{
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "username": "tu-email@gmail.com",
  "password": "tu-password",
  "use_tls": true,
  "from_email": "noreply@3f.com",
  "notifications": {
    "transaction_created": true,
    "budget_alert": true,
    "goal_reached": true,
    "login_attempt": true
  }
}
```

---

### 3. Dólar Hoy (`dolar_hoy`)

**Descripción:** Actualiza cotizaciones del dólar en Argentina

**Hooks:**
- `daily_summary`

**Fuentes:**
- Dólar Blue
- Dólar MEP (Bolsa)
- Dólar CCL (Contado con Liqui)
- Dólar Cripto

**Configuración:**
```json
{
  "sources": ["blue", "mep", "ccl"],
  "update_frequency": "hourly",
  "create_divisas_if_missing": true
}
```

---

## 🔌 API Endpoints

### Listar Plugins
```http
GET /api/plugins/
```

### Instalar Plugin
```http
POST /api/plugins/
Content-Type: application/json

{
  "nombre_tecnico": "mi_plugin",
  "nombre_display": "Mi Plugin",
  "descripcion": "Descripción del plugin",
  "version": "1.0.0",
  "autor": "Tu Nombre",
  "configuracion": {},
  "hooks": ["transaction_created"]
}
```

### Activar Plugin
```http
POST /api/plugins/{id}/activar
```

### Desactivar Plugin
```http
POST /api/plugins/{id}/desactivar
```

### Actualizar Configuración
```http
PUT /api/plugins/{id}/config
Content-Type: application/json

{
  "bot_token": "nuevo-token",
  "chat_id": "nuevo-chat"
}
```

### Ver Estado
```http
GET /api/plugins/{id}/estado
```

### Probar Plugin
```http
POST /api/plugins/{id}/test
```

### Listar Hooks
```http
GET /api/plugins/hooks/disponibles
```

---

## 🛠️ Crear un Nuevo Plugin

### 1. Estructura del Plugin

```python
# backend/plugins/mi_plugin/__init__.py
from .plugin import MiPlugin

__all__ = ["MiPlugin"]
```

```python
# backend/plugins/mi_plugin/plugin.py
from backend.plugins.base import BasePlugin

class MiPlugin(BasePlugin):
    nombre_tecnico = "mi_plugin"
    nombre_display = "Mi Plugin"
    version = "1.0.0"
    autor = "Tu Nombre"
    descripcion = "Descripción del plugin"
    hooks = ["transaction_created", "budget_alert"]
    
    async def initialize(self):
        """Inicializar el plugin"""
        self.validate_config(["api_key"])
        self.logger.info("Plugin inicializado")
    
    async def shutdown(self):
        """Cerrar el plugin"""
        self.logger.info("Plugin cerrado")
    
    async def on_transaction_created(self, transaction, user):
        """Manejar nueva transacción"""
        api_key = self.get_config("api_key")
        # Tu lógica aquí
        pass
    
    async def on_budget_alert(self, budget, percentage):
        """Manejar alerta de presupuesto"""
        pass
```

### 2. Hooks Disponibles

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

### 3. Métodos de BasePlugin

```python
# Obtener configuración
valor = self.get_config("clave", default="valor_default")

# Validar configuración requerida
self.validate_config(["api_key", "secret"])

# Obtener información del plugin
info = self.get_info()
```

### 4. Registrar Plugin

```bash
# Llamar a la API para registrar
curl -X POST http://localhost:8000/api/plugins/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "nombre_tecnico": "mi_plugin",
    "nombre_display": "Mi Plugin",
    "version": "1.0.0",
    "autor": "Tu Nombre",
    "hooks_suscritos": "transaction_created,budget_alert"
  }'

# Activar plugin
curl -X POST http://localhost:8000/api/plugins/1/activar \
  -H "Authorization: Bearer TOKEN"

# Configurar
curl -X PUT http://localhost:8000/api/plugins/1/config \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"api_key": "tu-api-key"}'
```

---

## 🧪 Testing

### Probar Plugin
```python
# En tests/test_plugins.py
import pytest
from backend.core.plugin_manager import plugin_manager
from backend.plugins.telegram_bot.plugin import TelegramBotPlugin

@pytest.mark.asyncio
async def test_telegram_plugin():
    plugin = TelegramBotPlugin(config={
        "bot_token": "test-token",
        "chat_id": "123456"
    })
    
    await plugin.initialize()
    
    # Simular hook
    await plugin.on_transaction_created(
        transaction=mock_transaction,
        user=mock_user
    )
```

---

## 📊 Flujo de Datos

```
Evento del Sistema
       ↓
PluginManager.call_hook()
       ↓
   Busca plugins suscritos
       ↓
Plugin.on_hook()
       ↓
Handler específico
       ↓
Lógica del plugin
```

---

## ⚙️ Configuración Avanzada

### Esquema JSON de Configuración

```python
# En tu plugin, define el esquema esperado:
{
  "api_key": {"type": "string", "required": True},
  "timeout": {"type": "integer", "default": 30},
  "enabled": {"type": "boolean", "default": True},
  "options": {
    "type": "array",
    "items": {"type": "string"}
  }
}
```

### Manejo de Errores

```python
async def on_transaction_created(self, transaction, user):
    try:
        # Tu lógica
        await self.api_call()
    except Exception as e:
        self.logger.error(f"Error: {e}")
        # No re-lanzar para no afectar otros plugins
```

---

## 🔒 Seguridad

- Los plugins se ejecutan en el mismo proceso
- Validar siempre la configuración
- No exponer secrets en logs
- Usar timeouts en llamadas externas
- Sanitizar inputs

---

## 📝 Ejemplos Comunes

### Notificación Slack

```python
async def on_budget_alert(self, budget, percentage):
    webhook_url = self.get_config("webhook_url")
    message = {
        "text": f"⚠️ Presupuesto excedido: {percentage}%"
    }
    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json=message)
```

### Backup Automático

```python
async def on_daily_summary(self, user, summary):
    if self.get_config("auto_backup"):
        await self.create_backup()
```

### Integración Bancaria

```python
async def on_account_sync(self, account, transactions):
    api = self.get_bank_api()
    new_transactions = await api.fetch_transactions(account.id)
    # Procesar transacciones...
```

---

## 🤝 Contribuir

1. Fork del repositorio
2. Crear plugin en `backend/plugins/`
3. Agregar tests
4. Documentar en este README
5. Pull request

---

## 📄 Licencia

MIT License - 3F Team 2026

---

## 📞 Soporte

- Documentación: [Wiki del proyecto]
- Issues: [GitHub Issues]
- Email: soporte@3f.com

---

**Versión:** 1.0.0  
**Última actualización:** Febrero 2026
