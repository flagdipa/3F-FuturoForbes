# Design: Estrategia de Auditoría Visual y Funcional

## Technical Approach
1. Iniciar el servidor Uvicorn en el puerto 8000.
2. Utilizar el browser agent para navegar a la URL base `http://localhost:8000`.
3. Recorrer metódicamente todos los módulos, capturando cualquier anomalía (Botón roto, estilo CSS faltante, error en consola F12).

## Error Reporting
Se generará el archivo `error_log_report.md` en la raíz de este cambio (`openspec/changes/full-qa-audit-and-report/error_log_report.md`) siguiendo este formato:
- [ ] **ID de Error**: NombreDescriptivo (Prioridad: ALTA/MEDIA/BAJA).
- **Módulo**: Dashboard/Cuentas/Budgets/etc.
- **Descripción**: Comportamiento esperado vs real.
- **Evidence**: Foto o mensaje de consola.
