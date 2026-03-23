# Spec: Multi-Moneda (FX)

## Goal
Soportar globalidad total, donde el usuario puede abrir cuentas y transaccionar en USD, EUR, ARS, BTC paralelamente, utilizando una moneda "Base" de consolidación para reportes (Ej: Ver todo mi wealth unificado en USD).

## Data Models
### Currency
```python
class Currency(SQLModel, table=True):
    code: str = Field(primary_key=True) # ISO 4217, Ej "EUR"
    symbol: str # "€"
    exchange_rate: Decimal # vs DIVISA BASE LOCAL DEL USUARIO
    last_updated: datetime
```

## API Endpoints (`/api/v1/fx`)
- `GET /rates` - Mapeo de valores de conversión actuales.
- `POST /update` - Hookeado o programado (e.g., vía plugin dolar_hoy) para actualizar la row de BD.
- `POST /convert` - Calculadora al vuelo para mostrar pre-views en UI sin guardar en base.
