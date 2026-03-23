# Design: Estrategia de Verificación General y QA del Sistema

## Context
Tras concluir la fase de refactorización "Under-the-Hood", el sistema cuenta con nuevas rutas de backend y esquemas de datos V2. El frontend (HTML/JS) ha sido parcialmente adaptado, pero carece de un test de integración visual completo que garantice que todos los hooks (hooks_engine.py) y llamadas a API (ia.py, budgets/router.py, etc.) están sincronizados.

## Goals / Non-Goals
### Goals
- Confirmar que el flujo de Login y Navegación entre vistas funciona sin recargas fallidas.
- Validar la integración del nuevo modelo de Presupuestos (Name, lines[]) en la UI.
- Asegurar que el autocompletado de Transacciones vía OCR no produce errores 500.
- Identificar y documentar bugs visuales (estéticos, de layout o de componentes JS).

### Non-Goals
- Realizar pruebas de carga masiva (Stress Testing).
- Integrar nuevos componentes (Solo QA de los existentes).

## Technical Approach

### 1. Preparación del Entorno Testing
Se ejecutará el servidor `uvicorn` localmente en el puerto 8000, apuntando a una base de datos de prueba `3f_test.db` o la base de datos de desarrollo actual para verificar la migración de datos.

### 2. Metodología de Auditoría (Script de Navegación)
El agente de navegación realizará el siguiente recorrido lógico:
1.  **Auth**: Registro de nuevo usuario -> Login exitoso -> Redirección a Dashboard.
2.  **Configuración**: Creación de una Cuenta de Prueba y una Categoría de Prueba.
3.  **Transacciones**: Registro de una transacción con "Split" y carga de ticket (validando el log de Tesseract).
4.  **Budgets/Goals**: Creación de un presupuesto para el mes actual y una meta de ahorro corta. Contribuir a la meta.
5.  **Insights/Reports**: Navegar a la sección de reportes y verificar que los gráficos (Chart.js) renderizan con los datos cargados.

### 3. Registro de Errores (Error Log)
Cada fallo se documentará en un archivo `error_log.md` dentro de la carpeta del cambio, categorizándolo por:
- **Severidad**: Crítico (No permite avanzar), Mayor (Falla funcional), Menor (Estético solo).
- **Causa**: Error API (404/500), Fallo JS de Frontend, Inconsistencia de datos.

## Risks / Trade-offs
- **Dependencia de Assets**: El QA via browser depende de que los archivos estáticos (`/static`) se carguen correctamente. Si no lo hacen, el QA será limitado.
- **Tesseract Locales**: La prueba de OCR fallará si el usuario no tiene Tesseract instalado en local (se marcará como "expected" si no hay binario).
