# Tasks: Corrección de Desincronización Crítica

## 1. Fix de Rutas (ui_router.py)

- [x] 1.1 Agregar ruta `/configuracion` como alias de `/settings` en `ui_router.py`
- [x] 1.2 Agregar ruta `/cuentas` apuntando a `accounts/index.html` (verificar si ya existe y funciona)
- [x] 1.3 Agregar ruta `/presupuestos` como alias de `/budgets` en `ui_router.py`
- [x] 1.4 Agregar ruta `/inversiones` como alias de `/investments`
- [x] 1.5 Agregar rutas de sub-secciones: `/reportes/cashflow`, `/reportes/heatmap`, `/mercado/dolar`, `/mercado/crypto`
- [x] 1.6 Agregar ruta `/cuentas/reconciliar` compatible con la referencia en base.html

## 2. Fix de CSS Sidebar Collapse (neon-3f.css)

- [x] 2.1 Eliminar las reglas genéricas duplicadas `.sidebar-collapse .app-sidebar { width: 0; transform: translateX(-100%) }` (líneas ~413-421) que pisan las reglas del mini-sidebar desktop
- [x] 2.2 Verificar que las reglas dentro de `@media (min-width: 992px)` para `.sidebar-collapse` funcionan correctamente (width: 54px, iconos visibles y centrados)
- [x] 2.3 Verificar que el sidebar colapsado oculta el brand text

## 3. Fix de i18n (lang-es.json / lang-en.json)

- [x] 3.1 Agregar claves faltantes en `lang-es.json` dentro de `transactions.columns`: `tipo`, `fecha`, `hora`, `cuenta`, `beneficiario`, `categoria`, `monto`, `saldo`, `etiquetas`, `estado`, `is_split`
- [x] 3.2 Agregar las mismas claves en `lang-en.json` con valores en inglés

## 4. Fix del Menú Sidebar (base.html)

- [x] 4.1 Agregar sección "Catálogos" en el sidebar con accesos directos a Beneficiarios y Categorías (apuntando a los modales o a rutas dedicadas)
- [x] 4.2 Ocultar el brand text del sidebar (`SISTEMA 3F`) cuando está en modo colapsado usando la misma lógica CSS de `display: none` que se aplica a los textos de nav-links
- [x] 4.3 Verificar que el menú "Herramientas" del navbar superior siga funcionando como acceso alternativo

## 5. Validación

- [x] 5.1 Reiniciar el servidor uvicorn y verificar manualmente que todas las rutas del sidebar devuelven HTTP 200
- [x] 5.2 Verificar que el sidebar colapsado muestra iconos correctamente en desktop
- [x] 5.3 Verificar que la tabla de transacciones muestra los headers traducidos correctamente
