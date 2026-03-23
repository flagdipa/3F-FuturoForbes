## Why
El usuario necesita una mayor trazabilidad y organización para los documentos adjuntados en la Bóveda Digital. Para lograrlo, los archivos deben nombrarse de manera estandarizada y guardarse en rutas elegibles por el usuario, lo cual demanda introducir códigos de identificación en las cuentas y beneficiarios del Core Financiero.

## What Changes
1. **Bóveda Digital**: 
   - Capacidad de elegir el directorio/carpeta destino del archivo físico.
   - Guardado estricto de la ruta completa (`path` o `directory`) asociado al `Attachment`.
   - Motor de renombrado automático usando el timestamp y los códigos de las partes. Formato objetivo: `YYMMDD_hhmm_<codigo_cuenta_origen>_<codigo_cuenta_destino>_<beneficiario>`.
2. **Core Financiero**:
   - Agregar de forma obligatoria o precargada un campo `code` (código corto o identificador) para cada `Account` y cada `Beneficiary` en el momento de su creación.

## Capabilities
### Modified Capabilities
- `boveda-digital`: Lógica de renombrado y ruteo de archivos.
- `core-financiero`: Nuevos campos unívocos para entidades financieras y sus endpoints de creación.

## Impact
- **Base de datos**: Migrar esquemas `accounts` y `beneficiaries` agregando columna `code`.
- **API**: `/vault` y los mutadores de cuentas/beneficiarios deben validar y procesar estos nuevos datos de nomenclatura.
