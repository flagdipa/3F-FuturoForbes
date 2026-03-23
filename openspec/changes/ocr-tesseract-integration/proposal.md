# Proposal: OCR Restoration with Pytesseract

## Problem Context
El sistema 3F (Futuro Forbes) cuenta con un módulo de escaneo de tickets (IA OCR) que actualmente depende exclusivamente de PaddleOCR. Si bien este motor es potente, consume muchos recursos y puede fallar bajo condiciones de imagen no ideales. No existe un mecanismo de redundancia local que sea liviano y fácil de configurar. Se ha descartado el uso de Google Gemini por ahora, por lo que necesitamos una alternativa local confiable que actúe como respaldo o incluso motor primario en entornos con pocos recursos.

## Proposed Solution
Se propone integrar `pytesseract` (Python wrapper para Tesseract-OCR) como el motor de fallback principal (o primera instancia de respaldo) del sistema. Esto implica:
1.  **Configuración de Tesseract**: Asegurar que el binario de Tesseract esté accesible en Windows (usualmente en `C:\Program Files\Tesseract-OCR\tesseract.exe`).
2.  **Extracción Estructurada**: Implementar un servicio de parseo heurístico que tome el texto crudo de Tesseract y extraiga:
    *   Monto total (buscando patrones de moneda y números).
    *   Fecha de transacción (detectando formatos DD/MM/YYYY o ISO).
    *   Establecimiento (primeras líneas legibles del ticket).
3.  **Integración en API**: Actualizar el `ia_ocr/services.py` para priorizar Tesseract cuando PaddleOCR falle, eliminando la dependencia de Gemini.

## Impact
- **Disponibilidad Offline**: El sistema podrá procesar tickets sin conexión a internet ni claves de API externas.
- **Robustez**: Mayor probabilidad de obtener resultados aunque el motor principal de Deep Learning (Paddle) falle.
- **Simplicidad**: Pytesseract es un estándar de la industria para OCR ligero.
- **Consumo de Recursos**: Menor huella de memoria que PaddleOCR para escaneos rápidos.
