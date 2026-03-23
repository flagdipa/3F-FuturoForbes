# Proposal: System Stabilization V2

## Overview

Este cambio aborda la deuda técnica y los errores críticos acumulados durante el despliegue de la arquitectura **Sistema 3F (FuturoForbes) V2**. El enfoque principal es la estabilización del entorno reactivo (Alpine.js), la finalización de la infraestructura de internacionalización (i18n) y la reparación de los flujos de negocio fundamentales en los módulos de Transacciones y Programadas.

## Motivation

Tras la migración inicial a FastAPI y el rediseño inspirado en MMEX para el frontend con Alpine.js, han surgido problemas sistémicos de **integridad de estado y tiempo de ejecución**:

1.  **Alpine JS Race Conditions**: Los componentes de página (vía `extra_js`) intentan registrarse o acceder a almacenes (`$store.benefManager`) antes de que los scripts globales o el propio Alpine estén listos, lo que resulta en errores de de definición y botones inoperantes.
2.  **Módulo de Transacciones Quebrado**: Varias funciones críticas (`newTransaction`, `editTransaction`) se han perdido del scope durante las ediciones o no se inyectan correctamente en el componente.
3.  **Inconsistencia de i18n**: Aunque el motor básico funciona, no hay coherencia total en las etiquetas de la aplicación, con claves técnicas visibles como `nav.currencies` o `goals.no_goals`.
4.  **Error 500 en Programadas**: La ruta de `/programadas` (Backend) está incompleta o mal enrutada en la V2 de SQLModel.

## Proposed Changes

1.  **Frontend Initialization Architecture**:
    *   Estandarizar el orden de carga en `base.html` utilizando scripts core en el HEAD con el atributo `defer` y cargando Alpine.js al final del BODY también con `defer` para garantizar que todos los `alpine:init` y registros locales se completen antes de que Alpine tome el control del DOM.
    *   Inyectar logs de diagnóstico durante el registro de componentes para auditar fallos de inicialización.

2.  **Módulo de Transacciones (Repair & Sync)**:
    *   Restaurar la lógica de gestión de transacciones dentro del componente `transaccionesPage`.
    *   Asegurar que los filtros y la carga paginada funcionen correctamente tras el fix de los stores.

3.  **Backend Routing & Models Integration**:
    *   Implementar e integrar el router `backend/api/v1/recurring.py` para resolver las peticiones de transacciones recurrentes.
    *   Verificar que `SQLModel` maneje correctamente las relaciones de las tablas de recurrencia en línea con la arquitectura V2.

4.  **Complete i18n Sync**:
    *   Consolidar y auditar `lang-es.json` y `lang-en.json` para eliminar claves raw del sidebar, tablas y modales.

## Impact

*   **Front-end**: Mejora drástica en la estabilidad de la SPA. Eliminación de errores de consola "undefined".
*   **Negocio**: Los usuarios podrán volver a crear y gestionar transacciones y tareas programadas sin fallos críticos de interfaz.
*   **Mantenibilidad**: Se establece un patrón de carga de scripts robusto que previene futuras regresiones de scope.
