# Design: OCR Restoration with Pytesseract

## Context
El sistema cuenta con una arquitectura de IA de tres capas: PaddleOCR (local, pesado), Gemini (nube, de pago/clave API) y Tesseract (local, ligero). Por decisiones de arquitectura, se desactivará Gemini y se potenciará Tesseract para suplir las carencias del motor principal cuando éste sea demasiado pesado o falle en su despliegue inicial. El mayor reto en Tesseract es la falta de estructura JSON nativa, por lo que el diseño se enfoca en el "Text-to-JSON parsing" mediante heurísticas locales.

## Goals / Non-Goals
### Goals
- Integrar `pytesseract` configurando el path binario en Windows.
- Implementar extracción heurística de Monto y Fecha usando Regex avanzados.
- Eliminar por completo el soporte de Gemini en el módulo `ia_ocr` para simplificar el flujo.
- Asegurar que el frontend siga recibiendo el formato `OcrResult` esperado por el `Main-Form`.

### Non-Goals
- Desarrollar un modelo de Deep Learning propio para OCR.
- Soportar PDFs de miles de páginas (solo tickets de imagen/pdf corto).

## Technical Approach

### 1. Configuración de Binarios
En el archivo `.env` se añadirá `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe`. Durante la inicialización del `OcrService`, se validará la existencia del ejecutable para evitar excepciones en tiempo de ejecución.

### 2. Cadena de Procesamiento (Heurística)
1. **Limpieza de Texto**: Remover caracteres extraños, espacios dobles y normalizar puntuación.
2. **Amount Detection**:
   *   Buscar líneas que contengan "TOTAL", "SUMA", "IMPORTE" o "PAGAR".
   *   Extraer el número mayor encontrado cerca de esas etiquetas.
   *   Heurística de seguridad: si no hay etiquetas, buscar el mayor número con formato monetario (Decimal) en las últimas 3 líneas del texto.
3. **Date Detection**:
   *   Regex para `DD/MM/YYYY`, `DD-MM-YYYY` y `YYYY-MM-DD`.
   *   Normalización de años de 2 dígitos a 4 (ej: `24` -> `2024`).
4. **Merchant/Payee**:
   *   La primera línea no nula del texto limpio suele ser el nombre del negocio o razón social.

### 3. Modificación del Flujo de Fallback
Se reescribirá `OcrService.process_image` para:
1. Intentar **PaddleOCR** (si está disponible y activo).
2. De fallar o no estar presente, intentar **Pytesseract**.
3. El motor de Gemini será removido del código de servicios.

## Risks / Trade-offs
- **Precisión**: Tesseract sin pre-procesamiento de imagen es inferior a modelos de visión modernos. Se mitigará recomendando al usuario buenas fotos (luz cenital, sin sombras).
- **Dependencia de Sistema**: Requiere que el usuario tenga instalado el ejecutable de Tesseract en su máquina. Se incluirá guía de instalación.
