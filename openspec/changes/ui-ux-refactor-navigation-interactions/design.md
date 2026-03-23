# Design: Refactor de Navegación e Interacciones UI/UX

## Context

El sistema 3F presenta algunas inconsistencias menores en la interfaz y navegación que afectan la experiencia del usuario (UX). Los botones de acción no tienen tamaños uniformes, las tablas no responden al doble clic para edición (un estándar de la industria), y el sidebar está sobrecargado con accesos a catálogos que deberían estar en un menú de gestión global.

## Goals

*   **Alineación de Botones:** Lograr que los botones de acción principal en el footer de las vistas tengan un ancho mínimo y alineación consistente.
*   **Interacción de Tabla:** Habilitar el doble clic en filas de transacciones para disparar la edición. Consolidar el código JS duplicado que causa conflictos.
*   **Limpieza de Sidebar:** Remover el grupo "Catálogos" del sidebar para simplificar la navegación lateral.
*   **Nuevo Menú de Entidades:** Crear un menú desplegable en la barra superior llamado "Entidades y Cuentas" (con ícono de banco/entidad) que contenga la gestión de Beneficiarios, Categorías y Cuentas.

## Non-Goals

*   Rediseñar completamente el sistema de temas Neon.
*   Cambiar la lógica de negocio de las transacciones o cuentas.

## Proposed Changes

### 1. Estilos CSS (neon-3f.css)
Introducir una clase de utilidad para botones de acción:
```css
.btn-action-standard {
    min-width: 120px;
    display: inline-flex;
    justify-content: center;
    align-items: center;
    text-align: center;
}
```
Aplicar flexbox en el contenedor de botones para asegurar que se distribuyan uniformemente.

### 2. Consolidación JS (transactions.js)
Eliminar la definición duplicada de `editTransaction`. Usar una única función robusta que maneje tanto el objeto de la fila como la carga desde la API si es necesario, asegurando compatibilidad con el evento `@dblclick`.

### 3. Reorganización de Base Template (base.html)
*   **Topbar:** Renombrar el dropdown de herramientas a "Entidades y Cuentas". Actualizar ícono a `fa-building-columns`.
*   **Sidebar:** Eliminar el bloque `<li class="nav-item">...Catálogos...</li>`.
*   **I18n:** Asegurar que las nuevas etiquetas del menú tengan claves en `lang-es.json`.

## Risks / Trade-offs

*   **Riesgo:** Movilidad de elementos en el UI puede confundir a usuarios acostumbrados a la ubicación anterior de "Catálogos".
*   **Trade-off:** El mini-sidebar (colapsado) ahora será más limpio pero perderá los íconos de catálogos. Esto es aceptable ya que se accede a ellos desde el menú superior que es siempre visible.
