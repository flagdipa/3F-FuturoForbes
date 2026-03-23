# Spec: Activos e Inversiones

## Goal
Normalizar la arquitectura bajo la cual el sistema 3F contabiliza y trackea tanto activos físicos (Asset Wealth) como portafolios de inversión bursátil o criptográfica (StockWealth).

## Capabilities

Esta especificación cubre "activos-inversiones", un pilar que diferencia 3F de simples gestores de cajas.

1. **Gestión de Bienes Materiales (Assets):**
   - Soporta bienes físicos tangibles: Propiedades inmobiliarias (PROPERTY), vehículos (VEHICLE), equipos de trabajo (EQUIPMENT).
   - Motor de depreciación: Descuento algorítmico del valor de posesión en función al tiempo transcurrido (Ej: `depreciation_rate`).
   - Flujo de revaluación asíncrono para mantener actualizado el patrimonio neto sin involucrar una transacción en la cuenta bancaria `INCOME`.

2. **Gestión de Stock / Bolsa (StockInvestment):**
   - Diversificación completa: Posibilidad de agregar Acciones reales (STOCK), Fondos (FUND), ETFs, o activos digitales Cripto (CRYPTO).
   - Monitor de precios histórico: Registro en línea de tiempo (Price History) para permitir la evaluación de rendimiento de cartera.
   - Cálculo del Patrimonio (Wealth) o PnL (Pérdidas y Ganancias) combinando cantidad (`quantity`) multiplicada por `avg_price` de compra vs `current_price` de cotización.

## Data Models

Tablas independientes que extienden el cálculo del Patrimonio (Wealth Service).

### Asset (Activos Físicos)
```python
class Asset(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    name: str # ej. "Honda Civic 2024"
    asset_type: str # ENUM(PROPERTY, VEHICLE, EQUIPMENT, OTHER)
    purchase_date: date
    purchase_value: Decimal
    current_value: Decimal # Valor actualizado del activo
    depreciation_rate: Decimal # Porcentaje anual de pérdida de valor
    notes: str
```

### StockInvestment & History (Bolsa / Cripto)
```python
class StockInvestment(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    account_id: int = Field(foreign_key="account.id") # Cuenta desde la que se financió
    symbol: str # Ticker: AAPL, SPY, BTC
    name: str
    investment_type: str # ENUM(STOCK, ETF, FUND, CRYPTO, OTHER)
    quantity: Decimal # Ej: 0.05 BTC (Fraccional es mandatorio)
    avg_price: Decimal # Precio ponderado de compra
    current_price: Decimal # Última cotización conocida
    currency_code: str # Moneda de cotización

class StockPriceHistory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    stock_id: int = Field(foreign_key="stockinvestment.id")
    date: date
    price: Decimal
```

## API Endpoints

Las operaciones están divididas en dominios tangibles e intangibles.

- **`/assets`**
  - `GET /` - Listado con valor depreciado al día actual.
  - `POST /` - Almacenamiento de nuevo activo material.
  - `GET /{id}` - Detalles de adquisición.
  - `PUT /{id}`, `DELETE /{id}`
  - `POST /{id}/revalue` - Actualización manual (o vía bot inmobiliario futuro) del `current_value` aislandolo del cálculo puramente matemático.

- **`/stocks`**
  - `GET /` - Listar cartera y posiciones abiertas sumando PnL.
  - `POST /` - Adicionar ticket de compra.

*(Nota: Historial y estadísticas financieras del portafolio se piden a nivel global en el endpoint de reportes, ej: `/reports/wealth` cubierto en specs transversales de reportabilidad).*

## Scenarios

- **Scenario: Depreciación de un Vehículo**
  - *Given* un `Asset` de tipo `VEHICLE` agregado el año previo valuado en $20000 con un `depreciation_rate` del 10% anual.
  - *When* un servicio llama a `/assets/1` o el reporte global del wealth solicita el valor.
  - *Then* se calcula al vuelo o se recupera el valor amortizado ($18000), sin ensuciar la cadena original de auditoría, para proyectar el Patrimonio Neto (Net Worth) correctamente en el Dash.
