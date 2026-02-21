# Plugin CriptoYa Multi-País

Plugin para 3F (Futuro Forbes) que obtiene cotizaciones de criptomonedas de la API de CriptoYa para múltiples países latinoamericanos.

## 📋 Características

- ✅ **11 Países soportados**: Argentina, Bolivia, Brazil, Chile, Colombia, República Dominicana, México, Perú, Paraguay, Uruguay, Venezuela
- ✅ **Múltiples Exchanges**: Obtiene datos de más de 40 exchanges locales
- ✅ **Criptomonedas principales**: BTC, ETH, USDT, USDC, DAI, SOL, BNB, XRP y más
- ✅ **Datos históricos**: Almacena cotizaciones para análisis temporal
- ✅ **Comisiones de retiro**: Registra fees por exchange y red
- ✅ **Mejor precio**: Identifica automáticamente el mejor exchange para comprar/vender
- ✅ **Alertas de precio**: Sistema de notificaciones configurable
- ✅ **Favoritos**: Permite marcar pares de trading preferidos

## 🚀 Instalación

### 1. Instalar Dependencias

```bash
cd backend/plugins/criptoya_multi
pip install -r requirements.txt
```

### 2. Registrar el Plugin

```bash
cd ../../../
python scripts/register_criptoya_plugin.py
```

### 3. Crear Tablas en Base de Datos

El plugin creará automáticamente las tablas necesarias al inicializarse. Asegúrate de que las migraciones estén aplicadas:

```bash
# Si usas Alembic
alembic upgrade head

# O reinicia el sistema para crear las tablas automáticamente
```

### 4. Configurar el Plugin

Vía API:
```bash
# Obtener ID del plugin
GET /api/plugins/

# Actualizar configuración
PUT /api/plugins/{id}/config
{
  "enabled": true,
  "paises": ["AR", "BR", "CL", "CO", "MX"],
  "coins": ["BTC", "ETH", "USDT", "USDC", "SOL"],
  "volumen_default": 0.1,
  "update_interval_minutes": 5,
  "auto_update": true,
  "notificar_cambio_significativo": true,
  "umbral_cambio_porcentaje": 5.0
}
```

### 5. Activar el Plugin

```bash
POST /api/plugins/{id}/activar
```

## 🌍 Países Soportados

| Código | País | Moneda | Status |
|--------|------|--------|--------|
| AR | 🇦🇷 Argentina | ARS | ✅ Activo |
| BO | 🇧🇴 Bolivia | BOB | ✅ Activo |
| BR | 🇧🇷 Brazil | BRL | ✅ Activo |
| CL | 🇨🇱 Chile | CLP | ✅ Activo |
| CO | 🇨🇴 Colombia | COP | ✅ Activo |
| DO | 🇩🇴 República Dominicana | DOP | ✅ Activo |
| MX | 🇲🇽 México | MXN | ✅ Activo |
| PE | 🇵🇪 Perú | PEN | ✅ Activo |
| PY | 🇵🇾 Paraguay | PYG | ✅ Activo |
| UY | 🇺🇾 Uruguay | UYU | ✅ Activo |
| VE | 🇻🇪 Venezuela | VES | ✅ Activo |

## 💱 Criptomonedas Soportadas

### Principales
- **BTC** - Bitcoin
- **ETH** - Ethereum
- **USDT** - Tether
- **USDC** - USD Coin
- **DAI** - Dai Stablecoin

### Altcoins Populares
- **SOL** - Solana
- **BNB** - BNB
- **XRP** - XRP
- **ADA** - Cardano
- **AVAX** - Avalanche
- **DOGE** - Dogecoin
- **MATIC** - Polygon
- Y más de 30 criptomonedas adicionales...

## 📊 Tablas de Base de Datos

El plugin crea las siguientes tablas nuevas (sin modificar tablas existentes):

### 1. criptoya_config
Configuración del plugin por usuario.

```sql
- id_config (PK)
- id_usuario (FK → usuarios.id_usuario)
- paises_habilitados (JSON)
- coins_monitoreadas (JSON)
- auto_update (bool)
- update_interval_minutes (int)
- volumen_default (decimal)
```

### 2. criptoya_paises
Catálogo de países soportados.

```sql
- id_pais (PK)
- codigo_iso (unique)
- nombre
- moneda_local
- disponible (bool)
```

### 3. criptoya_exchanges
Exchanges disponibles por país.

```sql
- id_exchange (PK)
- id_pais (FK → criptoya_paises.id_pais)
- slug (nombre técnico)
- nombre
- tipo (exchange, p2p, banco)
- activo (bool)
```

### 4. criptoya_coins
Criptomonedas disponibles.

```sql
- id_coin (PK)
- symbol (unique)
- nombre
- tipo (crypto, stablecoin)
- popular (bool)
```

### 5. criptoya_rates
Cotizaciones históricas.

```sql
- id_rate (PK)
- id_pais (FK)
- id_exchange (FK)
- id_coin (FK)
- fiat (ARS, BRL, etc.)
- ask, bid, totalAsk, totalBid (decimal)
- spread, spread_porcentaje (decimal)
- timestamp_api (int)
- creado_el (datetime)
```

### 6. criptoya_fees
Comisiones de retiro.

```sql
- id_fee (PK)
- id_exchange (FK)
- id_coin (FK)
- red (ERC20, BEP20, etc.)
- comision (decimal)
```

### 7. criptoya_alertas
Alertas de precio por usuario.

```sql
- id_alerta (PK)
- id_usuario (FK → usuarios.id_usuario)
- id_coin (FK)
- id_pais (FK)
- tipo (mayor_que, menor_que)
- valor_objetivo (decimal)
- activa (bool)
```

### 8. criptoya_favoritos
Pares de trading favoritos.

```sql
- id_favorito (PK)
- id_usuario (FK)
- id_coin (FK)
- id_pais (FK)
- fiat
- orden (int)
```

## ⚙️ Configuración

### Opciones Disponibles

| Opción | Tipo | Default | Descripción |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Habilitar/deshabilitar plugin |
| `paises` | array | `["AR"]` | Lista de códigos de países a monitorear |
| `coins` | array | `["BTC","ETH"]` | Criptomonedas a monitorear |
| `volumen_default` | decimal | `0.1` | Volumen de referencia para cotizaciones |
| `update_interval_minutes` | int | `5` | Intervalo mínimo entre actualizaciones |
| `auto_update` | boolean | `true` | Actualizar automáticamente vía hook daily_summary |
| `notificar_cambio_significativo` | boolean | `false` | Notificar cambios > umbral |
| `umbral_cambio_porcentaje` | decimal | `5.0` | Porcentaje de cambio para notificar |

## 🔌 Hooks

### `daily_summary`
Actualiza cotizaciones automáticamente según el intervalo configurado.

### `account_sync`
Puede disparar actualizaciones si la cuenta sincronizada es de cripto.

## 📡 API Endpoints

El plugin no expone endpoints directos, pero puedes acceder a los datos vía:

```python
# Desde otros componentes del sistema
from backend.core.plugin_manager import plugin_manager

plugin = plugin_manager.get_plugin_instance("criptoya_multi")

# Obtener mejor precio
mejor_precio = plugin.obtener_mejor_precio("AR", "BTC", "ARS", "compra")

# Obtener estadísticas
stats = plugin.get_estadisticas()
```

## 🔧 Métodos Disponibles

### obtener_cotizacion_general(pais, coin, fiat, volumen)
Obtiene cotizaciones de todos los exchanges para un par específico.

### obtener_comisiones(pais)
Obtiene comisiones de retiro actualizadas.

### obtener_mejor_precio(pais, coin, fiat, tipo)
Encuentra el mejor exchange para comprar o vender.

### crear_alerta(user_id, coin, pais, fiat, tipo, valor)
Crea una alerta de precio.

### get_estadisticas(pais)
Retorna estadísticas de uso del plugin.

## 📝 Logs

El plugin registra información detallada:

- **INFO**: Inicialización, actualizaciones exitosas, estadísticas
- **WARNING**: Países no disponibles, coins no encontradas
- **ERROR**: Errores de API, problemas de BD
- **DEBUG**: Cotizaciones individuales, queries

## 🔄 Flujo de Trabajo

```
1. Plugin inicializado → Crea datos base (países, coins)
        ↓
2. Hook daily_summary ejecutado
        ↓
3. Verifica si toca actualizar (intervalo configurado)
        ↓
4. Consulta API CriptoYa para cada par país/coin
        ↓
5. Guarda cotizaciones en criptoya_rates
        ↓
6. Actualiza exchanges en criptoya_exchanges
        ↓
7. (Opcional) Verifica alertas y notifica usuarios
```

## 🛡️ Límites de API

- **Rate limit**: 120 requests por minuto
- **Actualización**: Datos se refrescan cada 1 minuto en la API
- **Recomendación**: No consultar más de 1 vez por minuto por par

## 🤝 Integración con Otros Componentes

### Divisas
Las cotizaciones pueden usarse para actualizar divisas tipo "crypto" en el sistema principal.

### Transacciones
Al registrar transacciones de cripto, se puede consultar el mejor precio disponible.

### Reportes
Los datos históricos permiten generar reportes de evolución de precios.

## 🐛 Troubleshooting

### "Error API: 429 Too Many Requests"
Reduce el `update_interval_minutes` o disminuye la cantidad de pares monitoreados.

### "País no encontrado"
Verifica que el código ISO esté en la lista de países soportados.

### No se guardan cotizaciones
Revisa los logs y verifica que las tablas estén creadas correctamente.

## 📄 Licencia

MIT License - 3F Team 2026

## 🔗 Enlaces

- [Documentación CriptoYa](https://docs.criptoya.com)
- [CriptoYa.com](https://criptoya.com)
- API Base URL: `https://criptoya.com/api`

---

**Versión**: 1.0.0  
**Compatibilidad**: 3F v1.0.0+  
**Última actualización**: Febrero 2026
