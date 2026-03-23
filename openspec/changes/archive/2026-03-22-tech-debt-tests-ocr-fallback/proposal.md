# Proposal: Tests Restoration & Gemini OCR Fallback

## Problem Context
A partir de la migración del sistema 3F (Futuro Forbes) a los modelos Pydantic/SQLModel V2, muchos módulos core cambiaron sus esquemas de base de datos. Esto provocó que la antigua suite de pruebas `pytest` fallara y tuviera que ser en su mayoría eliminada o desactivada temporalmente. Actualmente, los componentes subyacentes se están testeando de forma manual, y esto genera un claro riesgo de regresiones. Necesitamos levantar la barra de cobertura reactivando pruebas transaccionales (CRUD de `Transactions/Accounts` V2) utilizando fixtures in-memory aisladas en `conftest.py`.

En segunda instancia, nuestra solución de Inteligencia Artificial para el escaneo de tickets (OCR) depende exclusivamente de la librería PaddleOCR corriendo en modo local. Esto consume memoria RAM y puede fallar bajo ciertas distorsiones de tickets. No hay redundancia. Se planeó originalmente utilizar `GEMINI_API_KEY` como plan de respaldo (Fallback) para solicitar una extracción Cloud Zero-Shot en el caso en que el local engine dé un Exception.

## Proposed Solution
La propuesta resuelve estas deudas técnicas críticas simultáneamente:
1. **Tests Suite**:
   - Reestructurar de forma definitiva el archivo `backend/tests/conftest.py`. Debe crear la sesión Mock de BD y un cliente autenticado Mock.
   - Reimplantar `test_transactions_api.py` (crear transacción, crear split de cuenta, leer transacciones) validando aserciones V2.
2. **Gemini OCR Fallback**:
   - Implementar la llamada en el endpoint `/api/ia/ocr` capturando errores base, o alternativamente si PaddleOCR no lee correctamente los importes.
   - Mandar la imagen codificada en Base64 junto a un prompt rígido (System Prompt que exija un Output de JSON idéntico a lo que espera `transactions.html`). Ej: `{ date: "...", amount: "...", payee: "...", description: "..." }`.

## Impact
- **Capa Confianza Backend**: Pruebas automáticas restauran la confiabilidad de desarrollo antes de intentar cualquier plugin extra.
- **Fiabilidad IA**: Minimiza drásticamente los falsos positivos/negativos del lector OCR.
- Componentes UI ilesos: el frontend NO recibe alteraciones, ya que `/api/ia/ocr` devolverá el mismo payload, sea procesado local o analizado por Gemini.
