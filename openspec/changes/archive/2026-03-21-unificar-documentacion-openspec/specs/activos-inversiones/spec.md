## ADDED Requirements

### Requirement: Gestión de activos físicos con depreciación
El sistema SHALL permitir registrar activos físicos (propiedades, vehículos, equipos) con cálculo automático de depreciación.

#### Scenario: Crear activo físico
- **WHEN** un usuario crea un activo con purchase_value y purchase_date
- **THEN** el sistema SHALL calcular valor actual basado en depreciación
- **AND** SHALL aplicar tasa de depreciación anual configurada
- **AND** SHALL mantener historial de valoración

#### Scenario: Calcular depreciación
- **WHEN** se evalúa el valor actual de un activo
- **THEN** el sistema SHALL aplicar depreciación lineal
- **AND** SHALL usar fórmula: valor_actual = purchase_value - (purchase_value * tasa * años)
- **AND** SHALL actualizar automáticamente cada mes

#### Scenario: Revaluar activo
- **WHEN** un usuario actualiza current_value manualmente
- **THEN** el sistema SHALL registrar nueva valoración
- **AND** SHALL actualizar cálculos de patrimonio
- **AND** SHALL mantener historial de revalorizaciones

### Requirement: Seguimiento de inversiones (stocks, ETFs, cripto)
El sistema SHALL permitir seguir portafolio de inversiones con valorización en tiempo real.

#### Scenario: Registrar inversión en stock
- **WHEN** un usuario agrega una inversión con symbol, quantity, avg_price
- **THEN** el sistema SHALL calcular valor total de la posición
- **AND** SHALL asociarla a una cuenta de inversión
- **AND** SHALL comenzar a trackear precios

#### Scenario: Actualizar precios automáticamente
- **WHEN** el sistema obtiene precios actualizados de APIs externas
- **THEN** SHALL actualizar current_price de cada stock
- **AND** SHALL recalcular ganancias/pérdidas
- **AND** SHALL registrar historial de precios

#### Scenario: Calcular ganancias/pérdidas
- **WHEN** se muestra una inversión
- **THEN** el sistema SHALL calcular: ganancia = (current_price - avg_price) * quantity
- **AND** SHALL calcular porcentaje de retorno
- **AND** SHALL mostrar ganancia realizada vs no realizada

### Requirement: Tipos de inversión soportados
El sistema SHALL soportar: acciones, ETFs, fondos, criptomonedas y otros instrumentos.

#### Scenario: Crear inversión tipo CRYPTO
- **WHEN** un usuario selecciona investment_type=CRYPTO
- **THEN** el sistema SHALL permitir símbolos de criptomonedas
- **AND** SHALL usar precios de fuentes cripto (CriptoYa)
- **AND** SHALL soportar fracciones decimales de monedas

#### Scenario: Crear inversión tipo ETF
- **WHEN** un usuario selecciona investment_type=ETF
- **THEN** el sistema SHALL validar símbolo de ETF
- **AND** SHALL obtener precios de fuentes apropiadas
- **AND** SHALL calcular comisiones si aplica

### Requirement: Historial de precios
El sistema SHALL almacenar historial de precios de cada inversión para análisis de rendimiento.

#### Scenario: Registrar precio diario
- **WHEN** el sistema actualiza precios diariamente
- **THEN** SHALL guardar registro en StockPriceHistory
- **AND** SHALL incluir fecha y precio
- **AND** SHALL mantener datos históricos ilimitados

#### Scenario: Ver evolución de precios
- **WHEN** un usuario consulta historial de una inversión
- **THEN** el sistema SHALL mostrar gráfico de precios
- **AND** SHALL permitir seleccionar rango de fechas
- **AND** SHALL mostrar tendencias y volatilidad
