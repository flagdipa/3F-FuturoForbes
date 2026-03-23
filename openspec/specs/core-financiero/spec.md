# Spec: Core Financiero

## Goal
Centralizar y consolidar la documentación técnica y funcional de la capacidad "Core Financiero" del sistema 3F (Futuro Forbes), proveyendo una fuente única y estructurada sobre cómo se gestionan las cuentas, transacciones y presupuestos sin depender de documentos legado dispersos.

## Capabilities

Esta especificación cubre la gestión financiera base del sistema:

1. **Gestión de Cuentas:**
   - Tipos soportados: Bancarias (corrientes, ahorros), Efectivo, Tarjetas de crédito, Plazo fijo, Inversión, Préstamos, Billeteras Digitales / Virtuales, Criptomonedas, Metales, etc.
   - Asociación jerárquica a una Entidad Financiera (ej. Banco Francés).
   - Listado UI: Grillas o vistas de tabla tipo Ledger con columnas detalladas e clave/ícono de banco asociado.
   - Soporte multi-divisa.
   - Saldos actualizados en tiempo real mediante snapshot diario.

2. **Entidades Financieras (Institutions):**
   - Entidades financieras administrables con ABM gráfico (como Categorías), con su respectivo selector de íconos representativos en la UI.
   - Enlace relacional unívoco (ID/code) desde donde nacen y se asocian las cuentas bancarias o de la billetera virtual.
   - Campos: Nombre (name), Tipo (type), Ícono (icon), Usuario (user_id).

3. **Transacciones:**
   - Tipos: Ingresos, Egresos, Transferencias.
   - Estados de conciliación (Reconciliado/Pendiente).
   - "Split transactions" (Múltiples líneas de detalle).
   - Etiquetado múltiple y adjuntos asociados a tickets/facturas.
   - Transacciones recurrentes automatizadas o manuales.

4. **Jerarquía de Categorías:** 
   - Niveles principales y subcategorías autogestionables.
   - Niveles principales y subtipos de entidades financieras.
   - Asociación a colores y presupuestos con reglas de alerta.

5. **Red de Beneficiarios (Payees):**
   - Autocategorización: Reglas de asignación automática de categorías basadas en el nombre del beneficiario de destino/origen.

6. **Sistema de Presupuestos:**
   - Marcos de tiempo: Mensual, Anual o Rolling.
   - Control cruzado de gasto real vs presupuestado por familia de categorías, con generación de alertas proactivas ante excesos (alert_threshold).

## Data Models

Se apoyan en el ORM `SQLModel` mediante la infraestructura base en `backend/models`:

### User
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    hashed_password: str
    is_active: bool
    theme: str
    ...
```

### Account & Currency
```python
class Account(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    code: str = Field(unique=True, index=True) # Código corto identificador. Ej: "SANT01", "CASH"
    account_type: str # ENUM(CHECKING, SAVINGS, CASH, etc.)
    currency_code: str = Field(foreign_key="currency.code")
    initial_balance: Decimal
    current_balance: Decimal
    is_active: bool
    ...

### Beneficiary (Payees)
```python
class Beneficiary(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    code: str = Field(unique=True, index=True) # Código corto. Ej: "EDENO", "FIBER"
    name: str
```

### Transaction & RecurringTransaction
```python
class Transaction(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    transaction_type: str # ENUM(INCOME, EXPENSE, TRANSFER)
    amount: Decimal
    currency_code: str
    account_id: int = Field(foreign_key="account.id")
    category_id: Optional[int] = Field(foreign_key="category.id")
    beneficiary_id: Optional[int] = Field(foreign_key="beneficiary.id")
    status: str # ENUM(RECONCILED, PENDING)
    date: date
    ...
```

### Budget & BudgetCategory
```python
class Budget(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    type: str # ENUM(MONTHLY, ANNUAL, ROLLING)
    start_date: date
    end_date: Optional[date]
    ...

class BudgetCategory(SQLModel, table=True):
    budget_id: int = Field(foreign_key="budget.id")
    category_id: int = Field(foreign_key="category.id")
    amount: Decimal
    alert_threshold: Decimal # percentage for alerts
```

## API Endpoints

Las interfaces están divididas por dominio en la capa FastApi (`/api/v1`):

- **`/auth`**
  - `POST /register`, `POST /login`, `POST /refresh`
  - `GET /me`, `PUT /me`
- **`/institutions`**
  - `GET /`, `POST /`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`
- **`/accounts`**
  - `GET /`, `POST /`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`
  - `GET /{id}/balance`, `GET /{id}/history`, `POST /{id}/reconcile`
- **`/transactions`**
  - `GET /`, `POST /`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`
  - `POST /split`, `POST /import`, `GET /search`
- **`/categories`**
  - `GET /`, `POST /`, `GET /{id}`, `PUT /{id}`, `DELETE /{id}`, `GET /{id}/stats`
- **`/beneficiaries`**
  - `GET /`, `POST /`, `GET /{id}`, `GET /{id}/transactions`
- **`/budgets`**
  - `GET /`, `POST /`, `GET /{id}`, `GET /{id}/status`, `GET /{id}/report`

## Scenarios

- **Scenario: Sincronización de Saldo (Account Balance)**
  - *Given* un `Account` con saldo 1000 ARS.
  - *When* se ingresa un `Transaction` tipo `EXPENSE` de 100 ARS asociado a dicha cuenta.
  - *Then* la el saldo actual `current_balance` de la cuenta debe ser 900 ARS en tiempo real, reflejándose en el snapshot diario (`/accounts/{id}/balance`).

- **Scenario: Control de Alerta Presupuestaria**
  - *Given* un `Budget` mensual activo con un `BudgetCategory` límite de 50000 ARS y `alert_threshold` del 80% (40000 ARS).
  - *When* un egreso empuja el total de gasto mensual de la categoría a 42000 ARS.
  - *Then* el motor de transacciones dispara una alerta asíncrona hacia el servicio/plugin correspondiente (`budget_alert` hook).

- **Scenario: Transacción Dividida (Split Transaction)**
  - *Given* una compra de supermercado que contiene víveres (Groceries) y electrodomésticos (Electronics).
  - *When* el cliente utiliza el endpoint `POST /transactions/split` por 15000 ARS, asignando 10000 a Groceries y 5000 a Electronics.
  - *Then* el sistema genera 2 `Transaction` entries vinculadas semánticamente, pero manteniendo la auditoría atada a un saldo único de egreso financiero.

## UI Integrity & Reactivity

- **Global Alpine Store Initialization**
  - Al cargar la aplicación (ej. en `/transacciones` o `/dashboard`), los almacenes globales de Alpine.js deben estar registrados antes de que cualquier componente de página realice su ciclo de vida `init()`. Esto evita errores tipo "undefined" al buscar `$store.benefManager`.
- **Transaction Action Dispatchers**
  - Los botones de la barra de acciones en `/transacciones` (ID `btn-new-tx`) deben disparar las funciones del componente para abrir el `modalNuevo` reseteando interactividad adecuada en caso que sea un state de registro o edición.
