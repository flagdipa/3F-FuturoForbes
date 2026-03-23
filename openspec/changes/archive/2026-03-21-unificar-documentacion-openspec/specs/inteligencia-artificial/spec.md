## ADDED Requirements

### Requirement: OCR de tickets con Google Gemini
El sistema SHALL integrar Google Gemini 1.5 Flash para extraer información de tickets y facturas.

#### Scenario: Procesar imagen de ticket
- **WHEN** un usuario sube imagen de ticket a /ia/ocr
- **THEN** el sistema SHALL enviar imagen a Google Gemini API
- **AND** SHALL extraer: fecha, monto total, items, establecimiento
- **AND** SHALL retornar datos estructurados en JSON

#### Scenario: Integrar OCR en formulario de transacciones
- **WHEN** un usuario usa función "Escanear ticket" en formulario
- **THEN** el sistema SHALL abrir modal de subida de imagen
- **AND** SHALL procesar OCR automáticamente
- **AND** SHALL pre-llenar campos del formulario con datos extraídos

#### Scenario: Validar resultado de OCR
- **WHEN** se reciben datos del OCR
- **THEN** el sistema SHALL permitir editar campos antes de guardar
- **AND** SHALL mostrar confianza del reconocimiento
- **AND** SHALL permitir rechazar y reintentar

### Requirement: Forecasting de gastos
El sistema SHALL utilizar IA para proyectar gastos futuros basados en historial.

#### Scenario: Generar pronóstico de gastos
- **WHEN** un usuario solicita GET /ia/forecast
- **THEN** el sistema SHALL analizar historial de gastos
- **AND** SHALL usar modelos de forecasting
- **AND** SHALL retornar proyección para próximos 3-6 meses

#### Scenario: Comparar proyección vs presupuesto
- **WHEN** se muestra pronóstico junto a presupuesto
- **THEN** el sistema SHALL alertar si proyección excede presupuesto
- **AND** SHALL sugerir ajustes de gasto

### Requirement: Sugerencias de categorización automática
El sistema SHALL sugerir categorías basadas en descripción y beneficiario.

#### Scenario: Sugerir categoría al crear transacción
- **WHEN** un usuario ingresa descripción de transacción
- **THEN** el sistema SHALL analizar texto con IA
- **AND** SHALL sugerir categoría basada en patrones históricos
- **AND** SHALL mostrar probabilidad de la sugerencia

#### Scenario: Aprender de correcciones del usuario
- **WHEN** un usuario corrige categoría sugerida
- **THEN** el sistema SHALL registrar corrección
- **AND** SHALL mejorar modelo para futuras sugerencias
- **AND** SHALL usar reglas del beneficiario como input

### Requirement: Detección de duplicados
El sistema SHALL detectar transacciones potencialmente duplicadas.

#### Scenario: Detectar posible duplicado
- **WHEN** se crea nueva transacción
- **THEN** el sistema SHALL buscar transacciones similares (monto, fecha, beneficiario)
- **AND** SHALL alertar si encuentra posible duplicado
- **AND** SHALL permitir continuar o cancelar

#### Scenario: Configurar sensibilidad de detección
- **WHEN** un usuario ajusta configuración de IA
- **THEN** el sistema SHALL permitir ajustar qué tan estricta es la detección
- **AND** SHALL aplicar configuración a futuras detecciones
