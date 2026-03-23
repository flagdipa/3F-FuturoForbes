# Proposal: Estabilización Final V2 y Cleanup General

## Problem Context
Tras la auditoría general, se han detectado tres fallos críticos que impiden el uso normal del sistema en su estado actual (V2):
1.  **Inconsistencia de Base de Datos**: Los modelos Budgets y Goals en `models_v2.py` tienen columnas (como `created_at` o `is_completed`) que no existen en la base de datos `3f_app.db` local, causando Errores 500 en la API.
2.  **Roptura de Alpine JS**: Las vistas de transacciones no están inicializando los objetos globales necesarios (`editTx`, `isScanningReceipt`), lo que bloquea la interacción.
3.  **Localización Degradada**: Muchas etiquetas de la interfaz no se traducen debido a que el sistema de i18n no tiene las entradas para los nuevos módulos o no las encuentra.

## Proposed Solution
1. **Reinicio de Base de Datos**: Eliminar `3f_app.db` para que el sistema la recree desde cero usando los esquemas actualizados de `models_v2.py`. Esto garantiza 100% de alineación entre DB y Código.
2. **Corrección de Variables Alpine**: Asegurar que `static/js/transactions.js` y `static/js/app.js` inicializan correctamente los stores de Alpine en el orden correcto.
3. **Mantenimiento i18n**: Completar los archivos de localización para cubrir `nav.*`, `goals.*` y `budgets.*`.
4. **Cleanup Estético**: Remover el nombre hardcodeado "Fer21gon" y hacerlo dinámico basándose en la sesión activa.

## Impact
- **Sistema 100% Funcional**: Eliminación de todos los Errores 500 detectados.
- **UX Premium**: Una interfaz limpia, traducida y con interacciones fluidas (Alpine JS).
