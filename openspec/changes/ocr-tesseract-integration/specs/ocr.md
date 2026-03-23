# Specs: OCR Restoration with Pytesseract

## BDD Requirements

### Requirement: Tesseract Configuration & Fallback
- **GIVEN** que el sistema tiene instalado Tesseract-OCR y configurado en `.env`.
- **WHEN** el usuario sube una imagen de ticket a `/api/v1/ia/ocr`.
- **THEN** si PaddleOCR falla o no está disponible, el sistema debe delegar a Pytesseract de forma transparente.
- **AND THEN** debe retornar un JSON con los campos: `monto_total`, `fecha`, `establecimiento`.

### Requirement: Amount Parsing (Decimal Tolerance)
- **GIVEN** un texto crudo de OCR conteniendo "$ 1.250,50" o "TOTAL 1250.50".
- **WHEN** se ejecuta el servicio de parseo heurístico.
- **THEN** el campo `monto_total` debe ser extraído como el tipo numérico `1250.50`.
- **AND THEN** debe detectar el símbolo de pesos como moneda `ARS` por defecto si no hay otro indicador.

### Requirement: Date Extraction
- **GIVEN** un ticket con la fecha "15/03/24" o "2024-03-15".
- **WHEN** se procesa la imagen.
- **THEN** el campo `fecha` debe normalizarse a formato ISO `2024-03-15`.

### Requirement: Merchant Name Recognition
- **GIVEN** un texto de Tesseract donde la primera línea no nula es "SUPERMERCADO DIA %".
- **WHEN** se extrae la información.
- **THEN** el campo `establecimiento` debe ser "SUPERMERCADO DIA %" (o el primer nombre identificable).

### Requirement: Fallback Gracioso si no hay Tesseract
- **GIVEN** un entorno donde ni Paddle ni Tesseract están configurados.
- **WHEN** se intenta procesar una imagen.
- **THEN** el sistema debe responder con un error 500 informando que "Ningún motor de OCR está disponible. Contacte al administrador." en lugar de crashear.
