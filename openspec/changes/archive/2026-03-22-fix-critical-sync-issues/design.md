# Design: Corrección de Desincronización Crítica

## Context

El sistema 3F migró de PHP a FastAPI + Alpine.js + AdminLTE 4. Durante la migración, las capas quedaron desincronizadas: el HTML del menú apunta a rutas en español, el router de Python tiene rutas en inglés, el CSS tiene reglas conflictivas de collapse, y el i18n tiene claves que no coinciden con lo que el JS necesita.

## Goals / Non-Goals

**Goals:**
- Restaurar la navegación completa del sistema (todas las rutas del menú deben funcionar)
- Restaurar el comportamiento del mini-sidebar con iconos al colapsar en desktop
- Mostrar textos traducidos correctamente en los headers de la tabla de transacciones
- Agregar acceso directo a Beneficiarios y Categorías desde el sidebar

**Non-Goals:**
- Reescribir la arquitectura del sistema
- Cambiar el framework CSS o JS
- Reestructurar los endpoints de la API REST

## Design

### Fix A: Rutas `ui_router.py`

Agregar ruta alias en español para cada vista que `base.html` referencia. Las funciones redireccionan al mismo template.

| Ruta en `base.html` | Ruta actual en router | Acción |
|---|---|---|
| `/configuracion` | `/settings` | Agregar `/configuracion` |
| `/cuentas` | `/accounts` | Ya existe parcialmente, verificar |
| `/presupuestos` | `/budgets` | Agregar `/presupuestos` |
| `/cuentas/reconciliar` | `/accounts/{id}/reconcile` | Agregar alias compatible |
| `/reportes/cashflow` | No existe | Agregar ruta |
| `/reportes/heatmap` | No existe | Agregar ruta |
| `/mercado/dolar` | No existe | Agregar ruta |
| `/mercado/crypto` | No existe | Agregar ruta |
| `/inversiones` | No existe (`/investments`) | Agregar `/inversiones` |

### Fix B: CSS sidebar collapse

Eliminar las reglas genéricas conflictivas en `neon-3f.css` líneas 413-421:
```css
/* ELIMINAR estas reglas que pisan el mini-sidebar desktop */
.sidebar-collapse .app-sidebar {
    width: 0;
    transform: translateX(-100%);
}
.sidebar-collapse .app-sidebar {
    width: 0;
    overflow: hidden;
}
```

Las reglas correctas dentro de `@media (min-width: 992px)` (L107-141) ya definen el comportamiento deseado (width: 54px, iconos centrados, tooltip hover). Las reglas genéricas las pisan por cascada CSS.

### Fix C: Claves i18n

Agregar alias en español dentro de `transactions.columns` en ambos archivos JSON:

```json
"columns": {
    "tipo": "TIPO",
    "fecha": "FECHA",
    "hora": "HORA",
    "cuenta": "CUENTA",
    "beneficiario": "BENEFICIARIO",
    "categoria": "CATEGORÍA",
    "monto": "MONTO",
    "saldo": "SALDO",
    "etiquetas": "ETIQUETAS",
    "estado": "ESTADO",
    "is_split": "Dividida",
    // ... claves existentes se mantienen
}
```

### Fix D: Menú sidebar (base.html)

Agregar acceso directo a Beneficiarios y Categorías en el sidebar bajo una sección "Catálogos", además de verificar que la ruta de cuentas sea accesible.

## Risks / Trade-offs

- **Riesgo bajo**: Los cambios son aditivos (agregar rutas, agregar claves, eliminar reglas CSS conflictivas). No modifican lógica de negocio.
- **Trade-off**: Mantener rutas duplicadas (español/inglés) agrega superficie pero es necesario para no romper bookmarks existentes.
- **Deuda técnica**: Idealmente habría una convención única de naming para rutas.
