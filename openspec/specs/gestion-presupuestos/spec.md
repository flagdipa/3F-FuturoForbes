# Spec: Gestión de Presupuestos

## Goal
Formalizar y centralizar el módulo de presupuestos (Budgets) del sistema 3F, el cual permite a los usuarios limitar, organizar y monitorear gastos mediante alertas automáticas sobre familias de categorías específicas en diferentes ventanas de tiempo.

## Capabilities

Esta especificación cubre la capacidad "gestion-presupuestos":

1. **Gestión e Iteración de Tiempo:**
   - La ventana u horizonte de un presupuesto puede ser de tipo `MONTHLY` (mes calendario), `ANNUAL` (anual) o `ROLLING` (móvil, por ejemplo útil para períodos atados a cortes de tarjeta de crédito).

2. **Detalle por Categoría:**
   - Un usuario puede tener un presupuesto maestro de 1.000.000 ARS donde asigna topes específicos a categorías puntuales (ej. 200.000 a supermercado, 50.000 a entretenimiento).
   
3. **Monitorización Asíncrona:**
   - Cálculo automático del monto ejecutado ("gasto real") versus "presupuestado".
   - Alertas asíncronas vía hook (`budget_alert`) cuando una categoría en un presupuesto activo excede un porcentaje configurable llamado `alert_threshold` (por ejemplo, notificar al 80% o al 100%).

## Data Models

Persistencia mediante `SQLModel` en `backend/models/models.py`.

### Budget
```python
class Budget(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str # ej. "Presupuesto Operativo Q1"
    type: str # ENUM(MONTHLY, ANNUAL, ROLLING)
    start_date: date
    end_date: Optional[date]
    is_active: bool
```

### BudgetCategory
El detalle de asignación:
```python
class BudgetCategory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    budget_id: int = Field(foreign_key="budget.id")
    category_id: int = Field(foreign_key="category.id")
    amount: Decimal # Límite en moneda local de la cuenta base
    alert_threshold: Decimal # ej. 80.0 para disparar alerta al 80%
```

## API Endpoints

Interfaces HTTP bajo `/api/v1/budgets`:

- `GET /` - Listado de presupuestos del usuario.
- `POST /` - Creación de un nuevo horizonte de presupuesto.
- `GET /{id}` - Detalles de la entidad Budget.
- `PUT /{id}` - Renombrar/cambiar fechas de iteración.
- `DELETE /{id}` - Archivar presupuesto.
- `GET /{id}/status` - (Importante) Endpoint calculador que cruza operaciones reales de `/transactions` vs los topes de `BudgetCategory` y devuelve un semáforo de estado de cumplimiento actual.
- `GET /{id}/report` - Devuelve JSON estructurado para generar la vista analítica del frontend (ej. doughnut charts / progreso).

## Scenarios

- **Scenario: Alerta Temprana de Gasto en Supermercado**
  - *Given* un `Budget` activo mensual con una `BudgetCategory` asignada a "Combustible" por 50000 y un `alert_threshold` de 80.
  - *When* se ingresa de forma automática una transacción de egreso de 10000 que provoca que el total del mes ascienda a 45000 (90%).
  - *Then* la lógica del sistema (o un trigger de DB/ORM) invoca al servicio de notificaciones, y se envía una notificación push "Alerta: Haz consumido el 90% del presupuesto de Combustible".
