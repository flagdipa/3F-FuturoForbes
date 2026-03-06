# 🪝 Referencia de Hooks — Sistema 3F (Futuro Forbes)

El sistema de hooks permite a los plugins extender la funcionalidad del core sin modificar el código base. Inspirado en la arquitectura de PrestaShop, 3F utiliza un motor de despacho de eventos asíncrono con soporte para prioridades.

## 🛠 Cómo usar los Hooks

### 1. Escuchar un Hook (Plugin)
Dentro de la clase de tu plugin, usa el decorador `@hook_listener` o simplemente define un método con el nombre `hook_NombreDelHook`.

```python
from core.hooks_engine import hook_listener

class MiPlugin(BasePlugin):
    @hook_listener("after_create_transaction", priority=5)
    async def notificar_compra(self, transaction, **kwargs):
        print(f"Nueva transacción detectada: {transaction.description}")
```

### 2. Disparar un Hook (Core)
El core utiliza `dispatch_hook` para notificar a los plugins.

```python
from core.hooks_engine import dispatch_hook

await dispatch_hook("after_create_transaction", transaction=new_tx)
```

---

## 📋 Lista de Hooks Disponibles

### Core Financiero
| Hook | Momento | Argumentos |
| :--- | :--- | :--- |
| `before_create_transaction` | Antes de persistir en DB | `transaction_data` |
| `after_create_transaction` | Después de persistir en DB | `transaction` |
| `before_update_transaction` | Antes de modificar | `transaction_id`, `new_data` |
| `after_update_transaction` | Después de modificar | `transaction` |
| `action_reconcile_account` | Al conciliar una cuenta | `account_id`, `date` |
| `action_budget_exceeded` | Al superar un presupuesto | `budget`, `category`, `amount` |

### Sistema y Auth
| Hook | Momento | Argumentos |
| :--- | :--- | :--- |
| `action_user_login` | Login exitoso | `user` |
| `action_user_logout` | Cierre de sesión | `user_id` |
| `action_system_startup` | Al iniciar el servidor | `app` |
| `action_backup_complete` | Al finalizar backup | `file_path`, `status` |

### Interfaz de Usuario (Inyección de UI)
Los plugins pueden retornar strings de HTML o JSON para ser renderizados en el frontend.

| Hook | Ubicación | Uso común |
| :--- | :--- | :--- |
| `display_dashboard_top` | Arriba del dashboard | Widgets de resumen |
| `display_sidebar_bottom` | Final del menú lateral | Enlaces rápidos |
| `display_transaction_detail` | Detalle de transacción | Info extra del plugin |

### Datos y IA
| Hook | Momento | Argumentos |
| :--- | :--- | :--- |
| `action_fx_update` | Actualización de tasas | `rates`, `source` |
| `action_ocr_complete` | Ticket procesado | `raw_text`, `data_extracted` |
| `action_import_complete` | Fin de importación CSV/Excel | `count`, `errors` |

---

## ⚖️ Prioridades
- **1-5**: Prioridad crítica/alta (se ejecutan primero).
- **10**: Prioridad por defecto.
- **20+**: Prioridad baja (se ejecutan al final).

> [!TIP]
> Si tu plugin depende de que otro plugin ya haya procesado los datos, usa una prioridad más alta (número mayor).
