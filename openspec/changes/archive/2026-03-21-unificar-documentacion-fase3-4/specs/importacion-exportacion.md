# Spec: Importación y Exportación

## Goal
Habilitar mecanismos de In/Out de datos masivos para el sistema 3F, previniendo formatos restrictivos (Vendor Lock-in) y permitiendo onboarding transparente a usuarios de MMEX u otros MS Finanzas.

## Capabilities
1. **Onboarding / Import CSV:** Motor de mapeo de columnas dinámico. Permite leer .CSV y .XLSX inyectando bulk operations atadas a una fecha o categoría mapeada.
2. **Exportación Reportística (`pandas` + `reportlab`):**
   - Extracción tabulada plana a XLSX para accountants/contadores.
   - Generación de informes PDF estilizados usando jinja o canva de reportlab, mostrando métricas analizadas del endpoint `/reports`.

## API Endpoints
- `POST /transactions/import` - Lector serial de datos a BD.
- `POST /reports/export` - Exporta la visión actual, aplicando filtros de fecha desde el body.
