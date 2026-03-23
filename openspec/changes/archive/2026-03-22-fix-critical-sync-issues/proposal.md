# Proposal: Corrección de Desincronización Crítica entre Capas

## What

Corregir los 3 problemas fundamentales de sincronización entre capas que provocan que el sistema se vea roto para el usuario final:

1. **Rutas HTML ↔ Router Python desincronizadas**: El `base.html` usa rutas en español (`/configuracion`, `/cuentas`, `/presupuestos`) pero `ui_router.py` solo registra las rutas en inglés (`/settings`, `/accounts`, `/budgets`), causando errores 404.
2. **CSS del sidebar-collapse conflictivo**: Las reglas CSS genéricas (sin media query) fuerzan `width: 0` y `translateX(-100%)` al colapsar el sidebar, pisando las reglas desktop que deberían mantener un mini-sidebar con iconos de 54px.
3. **Claves i18n desincronizadas en Transacciones**: Los `col.key` de JavaScript usan nombres en español (`tipo`, `fecha`, `hora`, `cuenta`, etc.) pero el archivo `lang-es.json` solo tiene claves en inglés (`type`, `date`, `time`, `account`), haciendo que se muestren los paths crudos como texto.

## Why

El sistema es funcionalmente correcto — los endpoints API, la lógica de negocio y los templates existen y funcionan. Pero la desconexión entre las 3 capas (routing, CSS, i18n) hace que parezca completamente roto ante el usuario. Cada pantalla que intenta abrir falla por una razón distinta pero todas comparten la misma causa raíz: falta de sincronización post-migración.

**No es necesario reescribir nada.** Son fixes quirúrgicos en 3 archivos que restauran ~90% de la funcionalidad visible.

## Impact

- **`backend/api/ui_router.py`**: Agregar aliases de ruta en español para todas las vistas que el menú referencia.
- **`frontend/static/css/neon-3f.css`**: Eliminar reglas CSS duplicadas/conflictivas del sidebar collapse.
- **`frontend/static/js/lang-es.json`** + **`lang-en.json`**: Agregar las claves faltantes que el componente de transacciones necesita.
- **`frontend/templates/base.html`**: Potencialmente agregar ítems faltantes al sidebar (Beneficiarios, Categorías como acceso directo).
