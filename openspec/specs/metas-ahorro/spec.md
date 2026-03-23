# Spec: Metas de Ahorro

## Goal
Documentar la lógica algorítmica y los modelos correspondientes al sistema de "Goals" (Metas de Ahorro), permitiendo al usuario de 3F establecer objetivos financieros acumulativos con métricas y alertas de progreso.

## Capabilities

Esta especificación cubre la capacidad "metas-ahorro":

1. **Definición Clara y Estructurada:**
   - Un objetivo claro (Monto objetivo `target_amount` asociado a una divisa `currency_code` y fecha límite `target_date`).
   - Apoyo UI: Asignación de color (`hex`) e ícono para visuales ricas en la capa Frontend (Ej. Alpine/Gridstack Dashboard).

2. **Acumulación de Capital:**
   - Aporte directo: Posibilidad de "aportar" a la meta sin que esto deba estar ligado estrictamente al flujo formal de cuentas, pero actualizando el progreso visual (`current_amount`).
   
3. **Múltiples Metas en Paralelo:** 
   - El motor del sistema maneja una n-cantidad de metas simultáneas.
   - Envío asíncrono de eventos vía hooks del core (`goal_reached`) cuando el balance `current_amount` iguala o supera `target_amount`.

## Data Models

Persistencia ligada al módulo de Wealth en la infraestructura general.

### Goal
```python
class Goal(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str # ej. "Viaje a Japón"
    target_amount: Decimal # Monto objetivo real a alcanzar
    current_amount: Decimal # El track record actual acumulado
    currency_code: str # En qué moneda se evalúa (ISO 4217, Ej. JPY, USD)
    target_date: date # Fecha límite proyectada o 'deadline'
    color: str # hex (#FF00AA)
    icon: str # Font Awesome Class
    is_active: bool
```

## API Endpoints

Puntos de acceso en el router `/api/v1/goals`:

- `GET /` - Listar todas las metas activas con sus porcentajes de completitud precálculados en base a `current/target`.
- `POST /` - Declarar una meta nueva.
- `GET /{id}` - Detalles de la meta.
- `PUT /{id}` - Modificar monto objetivo o deadline temporal.
- `DELETE /{id}` - Borrar definitivamente (Soft delete si aplicable a configuración global).
- `POST /{id}/contribute` - Incrementar el `current_amount` enviando un body JSON con la métrica a aportar y el origen.

## Scenarios

- **Scenario: Contribución y Consecución de Meta**
  - *Given* una meta ("Comprar Laptop") configurada a `$1000` (`target_amount`) y que se encuentra actualmente en `$900` (`current_amount`).
  - *When* se dispara una petición válida en el REST API: `POST /goals/12/contribute` enviando un payload de `{"amount": 100}` asociado.
  - *Then* se incrementa el saldo a `$1000`, la meta pasa internamente y lógicamente a estado "completed" (100%), y el sistema emite el trigger `goal_reached` para que Plugins o sistemas de Email (SMTP/Telegram) envíen las felicitaciones correspondientes.
