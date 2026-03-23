## Context
Extensión directa a las especificaciones originales generadas para la gestión de attachments y el core bancario, apuntando ahora a un motor documental más robusto y localizable.

## Goals
- Soportar `code` como string unívoca en transaccionantes.
- Enforzar nomenclatura universal `YYMMDD_hhmm_ORIGEN_DESTINO.ext` en los archivos de la bóveda.
- Libre designación de carpeta destino (Folder Tree).

## Migration Plan
1. Alterar especificación `core-financiero` para dictaminar el uso de un campo identificador `code` en Modelos.
2. Alterar especificación `boveda-digital` ampliando las directivas sobre cómo renombrar los archivos subidos al vuelo.
3. Generar las tareas de código asociadas para la implementación física (migration script, fastapi schemas, etc).
