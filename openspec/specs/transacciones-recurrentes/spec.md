# Spec: Transacciones Recurrentes

## Goal
Formalizar la documentación para el motor de automatización temporal del sistema: `transacciones-recurrentes`, responsable de orquestar, ejecutar o simplemente notificar sobre eventos regulares pre-programados sin intervención humana constante.

## Capabilities

Esta especificación cubre "transacciones-recurrentes":

1. **Definición de Patrones Temporales y UI Calendario:**
   - Visualización y manejo mediante "Calendario Interactivo" (FullCalendar) mostrando puntos de cobros/pagos.
   - El front posee botones inmediatos rápidos (Crear, Borrar, Modificar).
   - Modal Editor (Clickable): Al hacer On-Click sobre una iteración o regla plasmada en el calendario, esta arroja un panel para editarla libre o cancelarla en segundos, al estilo MMEX.
   - Creación de frecuencias predefinidas: Diaria (`DAILY`), Semanal (`WEEKLY`), Mensual (`MONTHLY`), Anual (`YEARLY`) o incluso personalizadas (`CUSTOM`).

2. **Suscripción de Comportamiento:**
   - Auto-ejecución vs Aprobación Previa: Una transacción programada puede insertarse automáticamente en el ledger (`auto_execute = true`), o bien esperar mediante envío de notificación para que el usuario le de un "Ok" al débito.
   
3. **Manejo de Excepciones:**
   - Capacidad modular de "saltarse" (skip) una ejecución en la línea del tiempo (por ejemplo prescindir el pago de un alquiler o seguro un mes específico sin eliminar la regla base).
   - Fechas de corte: Condición `end_date` que culmina de forma programada automática el ciclo de vida del proceso recurrente una vez alcanzada.

## Data Models

Se trata de un payload serializado anexo al sistema central de transacciones.

### RecurringTransaction
```python
class RecurringTransaction(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    # Campos base de transacción
    transaction_type: str # ENUM(Withdrawal, Deposit, Transfer)
    account_id: int = Field(foreign_key="account.id")
    target_account_id: Optional[int]
    beneficiary_id: Optional[int]
    category_id: Optional[int]
    amount: Decimal
    notes: Optional[str]
    # Control de recurrencia
    frequency: str # ENUM(Daily, Weekly, Monthly, Yearly)
    interval: int # Ejemplo: cada 2 meses
    start_date: date
    next_date: date # proxima_fecha en la UI
    is_active: bool # activo
    auto_execute: bool
```

*(La tabla `Transaction` posee paralelamente un Foreign Key `recurring_transaction_id` que liga operaciones atómicas finalizadas con la regla padre algorítmica).*

## Interacción de Arquitectura

Al no poseer actualmente un endpoint REST expuesto de forma independiente documentado en la Tabla 6.1 (Generalmente gestionado intra-servicios o dentro del router core), funciona en el Background:
- **Scheduler (Cron/Celery/AsyncIO):**
  Un demonio o tarea recurrente (`backend/core/scheduler.py`) escanea la BD cada noche buscando `RecurringTransaction` donde `next_execution_date <= today`.
- Al encontrar hits:
  1. Si `auto_execute`: Inyecta la data que vive en `transaction_data` en el servicio nativo de Account/Transactions. Acto seguido reasigna matemáticamente la nueva `next_execution_date`.
  2. Si `not auto_execute`: Pasa al servicio de notificaciones un recordatorio de ejecución, y deja la transacción en estado latente "Pending" o a merced del frontend.

## Scenarios

- **Scenario: Ejecución de Suscripción a Netflix**
  - *Given* una `RecurringTransaction` programada mensualmente (`frequency=MONTHLY`, `interval=1`), `auto_execute = true`, cuyo `next_execution_date` es la fecha de hoy, conteniendo un payload en su JSON de $1500 hacia el Beneficiario "Netflix".
  - *When* el script calendarizado del Backend (`scheduler.py`) procesa la base a medianoche.
  - *Then* se genera un Request virtual interno equivalente al API que inserta automáticamente el egreso en la cuenta asociada en `transaction_data` y traslade el `next_execution_date` al día exacto del mes subsecuente.

## API Endpoints

Las interfaces están expuestas en la capa FastApi (`/api/v1`):

- **`/recurring`**
  - El backend expone la ruta `/api/v1/recurring/` consistente con el esquema de SQLModel V2.
  - `GET / recurring/`: Devuelve un JSON con la estructura: `{"data": [...], "status": "success"}` y contiene los campos `frequency`, `interval`, `start_date` y `next_date` formateados en ISO.
