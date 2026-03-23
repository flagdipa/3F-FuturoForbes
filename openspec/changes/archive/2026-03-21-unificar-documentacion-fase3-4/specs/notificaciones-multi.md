# Spec: Notificaciones Multicanal

## Goal
Mantener al usuario informado sobre métricas importantes, ejecuciones silenciosas desde el `Scheduler` o triggers de plugins externos, consolidando un "Centro de Notificaciones" en el header web y envíos Push off-site.

## Capabilities
1. **Notificaciones In-App:**
   - Bandeja de entrada persistente listando alertas de presupuesto (`BUDGET_ALERT`), metas conseguidas (`GOAL_REACHED`), o advertencias del sistema de seguridad (`SYSTEM`).
   - Gestión de estado: "Leído/No Leído".
2. **Eventing a Plugins:**
   - La misma creación de la Notificación en la base de datos dispara event pipelines para que plugins (`telegram_bot`, `email_smtp`) dupliquen la alerta en canales externos si el User así lo configuró.

## Data Models
### Notification
```python
class Notification(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    type: str # ENUM(BUDGET_ALERT, SYSTEM...)
    title: str
    message: str
    is_read: bool = Field(default=False)
    action_url: Optional[str] = None
    created_at: datetime
    read_at: Optional[datetime]
```

## API Endpoints (`/api/v1/notifications`)
- `GET /` - Listador paginado (con flag opcional solo-unread).
- `PUT /{id}/read`, `PUT /read-all` - Mark as read bulk vs individual.
- `GET /unread-count` - Endpoint poller para la burbuja de la navbar.
