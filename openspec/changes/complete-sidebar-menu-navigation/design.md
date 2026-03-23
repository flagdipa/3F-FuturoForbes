# Design: Complete Sidebar Navigation Menu

## Context
Actualmente, el framework visual `base.html` aloja un menú de solo 4 ítems: Dashboard, Transacciones, Programadas y Comprobantes. Funcionalidades críticas como Metas de Ahorro locales, Cuentas, Beneficiarios, Categorías (gestionables mediante modales) e Inversiones son accesibles internamente en ciertas sub-páginas o requiriendo tipeo manual en URL. 

Este diseño extiende la columna lateral integrando tanto enlaces directos (menús de 1 nivel) como menús anidados (Treeviews de AdminLTE) para ordenar estas opciones dentro del UX V2.

## Goals
- Mantener la cohesión estilística con AdminLTE 4 y las directivas AlpineJS (`$store.lang.t`).
- Habilitar tooltips automáticos en modo colapsado (`:data-label=...`).
- Incluir soporte para menús desplegables (`.nav-treeview`) en secciones lógicamente agrupadas (Cuentas, Reportes, Mercado).

## Menú Sugerido y Nomenclatura

| Sección Principal | Sub-items (Treeview) | Icono Principal sugerido |
|---|---|---|
| **Dashboard** | N/A | `fa-gauge-high text-primary` |
| **Transacciones** | N/A | `fa-receipt text-success` |
| **Reportes / Analítica** | Cashflow, Heatmap | `fa-chart-pie text-cyan` |
| **Cuentas** | Cuentas, Reconciliar | `fa-wallet text-indigo` |
| **Gestores (Herramientas)** | Beneficiarios, Categorías | `fa-toolbox text-light` |
| **Planificación** | Presupuestos, Metas de Ahorro | `fa-bullseye text-warning` |
| **Inversiones** | Inversiones | `fa-arrow-trend-up text-success` |
| **Mercado (APIs)** | Dólar Hoy, CriptoYa | `fa-globe text-primary` |
| **Documentos** | Comprobantes (Vault) | `fa-vault text-info` |
| **Configuración** | Configuración de usuario | `fa-sliders text-secondary` |

## Technical Implementation

### Template HTML (`base.html`)
Se añadirá a la lista dinámica `<ul class="nav sidebar-menu flex-column" data-lte-toggle="treeview">`.

Para los **submenús** (Treeview de AdminLTE), la estructura requerida es:
```html
<li class="nav-item">
    <a href="#" class="nav-link" :data-label="$store.lang.t('nav.accounts_group')">
        <i class="nav-icon fa-solid fa-wallet text-indigo"></i>
        <p>
            <span x-text="$store.lang.t('nav.accounts_group')">Cuentas</span>
            <i class="nav-arrow fa-solid fa-angle-right"></i>
        </p>
    </a>
    <ul class="nav nav-treeview">
        <li class="nav-item">
            <a href="/cuentas" class="nav-link">
                <i class="nav-icon far fa-circle"></i>
                <p x-text="$store.lang.t('nav.accounts_list')">Listado</p>
            </a>
        </li>
    </ul>
</li>
```

### JSON Lang files
Las traducciones serán añadidas a `frontend/static/js/lang-es.json` y `lang-en.json` bajo la rama `nav`.
Ejemplo:
- `"nav.reports": "Reportes"`
- `"nav.accounts_group": "Gestión Cuentas"`
- `"nav.beneficiaries": "Beneficiarios"`

### Eventos Alpine
Para Beneficiarios y Categorías, la navegación no carga una URL, sino que dispara un evento que abre el modal (ya incluidos en `base.html`):
`<a href="#" class="nav-link" @click.prevent="$dispatch('open-beneficiaries')">`
`<a href="#" class="nav-link" @click.prevent="$dispatch('open-categories')">`

## Risks
1. **Overflow Vertical:** Agregar tantos items puede provocar que menús con pantallas pequeñas no hagan scroll. Debemos asegurarnos de que el `.sidebar-wrapper` de AdminLTE incluya comportamiento de scroll natural (Overlayscrollbars).
2. **Tooltips en Sub-items:** AdminLTE Treeview funciona ocultando `<ul>` anidados, por lo que expandir un menú en modo colapsado suele requerir clics especiales o expande la sidebar. No afectará la versión móvil por los overlays.
