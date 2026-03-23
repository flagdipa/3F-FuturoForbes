# Spec: Inteligencia Artificial

## Goal
Dotar de capacidades cognitivas al sistema 3F mediante la integración agnóstica de Modelos de Lenguaje Grandes (LLMs). Independientemente del proveedor (Gemini, OpenAI, Anthropic, o modelos locales como Llama3), el sistema expondrá interfaces abstractas para OCR, predicción y ayuda al usuario.

## Capabilities

1. **Proxy Multi-Modelo:**
   - La arquitectura no depende de un solo servicio. Se utilizan adaptadores abstractos que permiten cambiar de motor de IA simplemente ajustando credenciales o URLs (BYOK - Bring Your Own Key).
   
2. **OCR y Parseo de Tickets:**
   - Envío de un payload binario (imagen de un ticket/factura en formatos `.jpg`, `.png`, `.pdf`, `.bmp`, `.webp`).
   - El modelo devuelve un JSON estandarizado con: Fecha, Monto Total, Comercio, Iva e Ítems para autocompletar el formulario de `/transactions`.
   - Soporte para rotación automática y pre-procesamiento de imagen.

3. **Sugestión y Auto-Categorización:**
   - Análisis de descripciones ambiguas (Ej. "Cena McDonalds") para sugerir de forma inteligente el tag o categoría apropiada basándose en el historial de ese usuario (RAG o prompt-tuning básico).

4. **Forecasting (Análisis Predictivo):**
   - Inserción de un JSON con tendencias de flujo de caja reciente al modelo.
   - Generación de proyecciones sobre gasto mensual o alertas anticipadas sobre probables rupturas de presupuesto.

## API Endpoints (`/api/v1/ia`)
- `POST /ia/ocr` - Recibe metadata/imagen, devuelve un esquema de transacción validado.
- `POST /ia/analyze` - Análisis genérico de finanzas semanales.
- `GET /ia/forecast` - Proyección futura sobre la persistencia actual.
- `POST /ia/suggest-category` - Clasificador ML/LLM para autocompletado on-typing.

## Scenarios
- **Scenario: Escaneo de Ticket con Llama Local**
  - *Given* el usuario sube un archivo `.jpg`, `.png`, `.pdf` o `.bmp` desde la webapp hacia el endpoint `/ia/ocr`, estando el sistema configurado para apuntar a un cluster local Llama.
  - *When* el servidor local analiza la imagen.
  - *Then* se devuelve un parseo preciso separando el total pagado y los empaquetados para rellenar los inputs del DOM de Alpine.js instantáneamente.
