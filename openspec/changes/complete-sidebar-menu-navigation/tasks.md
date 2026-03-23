# Tasks: Complete Sidebar Menu Navigation

## 1. Traducciones (i18n)
- [x] 1.1 Editar `frontend/static/js/lang-es.json` y `lang-en.json`: Agregar la rama `nav` con items faltantes (`reports`, `reports_cashflow`, `reports_heatmap`, `accounts_group`, `accounts_list`, `accounts_reconcile`, `tools`, `beneficiaries`, `categories`, `planning`, `budgets`, `goals`, `investments`, `market`, `market_dolar`, `market_crypto`, `settings`).

## 2. Modificaciones al Sidebar HTML
En `frontend/templates/base.html`, buscar la estructura `<ul class="nav sidebar-menu flex-column" ...>` e implementar los siguientes bloques:
- [x] 2.1 **Reportes (Treeview)**: Bloque con icono `fa-chart-pie text-cyan`, expandible con `Dashboard` y sub-items `Cashflow`, `Heatmap` (si aplica).
- [x] 2.2 **Cuentas (Treeview)**: Bloque con icono `fa-wallet text-indigo`, expandible con `Listado` (`/cuentas`) y `Reconciliar` (`#` u otra UI).
- [x] 2.3 **Ajustes de UI (Modales)**: Bloque "Herramientas" (o ítems directos) para `Beneficiarios` y `Categorías`. Redirigir onClick a `@click.prevent="$dispatch('open-beneficiaries')"` y equivalente de Categories (según Alpine).
- [x] 2.4 **Planificación**: Enlaces simples para `Presupuestos` (`/presupuestos`) y `Metas de Ahorro` (`/metas`) con iconos correspondientes (`fa-bullseye` y `fa-piggy-bank`).
- [x] 2.5 **Inversiones**: Enlace simple para `Inversiones` (`/inversiones`) o Stocks.
- [x] 2.6 **Mercado (Treeview)**: Bloque con icono `fa-globe`, expandible con items para `Dólar Hoy` (`/mercado/dolar`) y `Crypto` (`/mercado/crypto`).
- [x] 2.7 **Configuración**: Enlace en la parte baja (`fa-sliders text-secondary`) hacia `#` o `/configuracion`.

*Nota: Asegurar que TODO elemento `<a class="nav-link">` tenga `:data-label="$store.lang.t('nav.X')"` para que el CSS Tooltip existente (implementado en `fix-sidebar-collapsed-icons`) funcione.*

## 3. Validación Visual
- [x] 3.1 Cargar la URL raíz `/` y expandir manualmente cada `nav-treeview` para asegurar que las directivas `data-lte-toggle="treeview"` no rompen el HTML y abren las ramas.
- [x] 3.2 Colapsar el sidebar (icono hamburguesa) y posicionar el cursor sobre cada nuevo ítem para confirmar la aparición del Tooltip verde/azul del lado derecho y sin desbordes.
- [x] 3.3 Validar que el botón "Beneficiarios" y "Categorías" desde el nuevo Navbar abre las modales correspondientes en pantalla.
