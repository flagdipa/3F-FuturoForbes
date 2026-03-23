/**
 * widget-panel.js
 * Componente Alpine para el panel de widgets con checkboxes.
 * Persiste la selección en localStorage y sincroniza con el dashboard.
 */

const WIDGET_PANEL_KEY = '3f_active_widgets';

// Catálogo completo de widgets disponibles
const ALL_WIDGETS_CATALOG = [
    { id: 'widget-balance-total',       name: 'Balance Total',         icon: 'fa-coins',              category: 'Finanzas' },
    { id: 'widget-monthly-summary',     name: 'Resumen Mensual',       icon: 'fa-chart-pie',          category: 'Finanzas' },
    { id: 'widget-recent-transactions', name: 'Últimas Transacciones', icon: 'fa-list-ul',            category: 'Actividad' },
    { id: 'widget-dolar-hoy',           name: 'Cotizaciones',          icon: 'fa-dollar-sign',        category: 'Mercado' },
    { id: 'widget-ia-insights',         name: 'IA Insights',           icon: 'fa-brain',              category: 'Inteligencia' },
    { id: 'widget-quick-add',           name: 'Acceso Rápido',         icon: 'fa-bolt',               category: 'Herramientas' },
];

document.addEventListener('alpine:init', () => {
    Alpine.data('widgetPanel', () => ({
        open: false,
        activeWidgets: [],
        allWidgets: ALL_WIDGETS_CATALOG,

        init() {
            // Cargar selección guardada o defaults (todos activos)
            const saved = localStorage.getItem(WIDGET_PANEL_KEY);
            if (saved) {
                try { this.activeWidgets = JSON.parse(saved); }
                catch(e) { this.activeWidgets = ALL_WIDGETS_CATALOG.map(w => w.id); }
            } else {
                this.activeWidgets = ALL_WIDGETS_CATALOG.map(w => w.id);
                this._persist();
            }
        },

        isActive(widgetId) {
            return this.activeWidgets.includes(widgetId);
        },

        toggle(widgetId, enabled) {
            if (enabled) {
                if (!this.activeWidgets.includes(widgetId)) {
                    this.activeWidgets.push(widgetId);
                    this._addToDashboard(widgetId);
                }
            } else {
                this.activeWidgets = this.activeWidgets.filter(id => id !== widgetId);
                this._removeFromDashboard(widgetId);
            }
            this._persist();
        },

        _persist() {
            localStorage.setItem(WIDGET_PANEL_KEY, JSON.stringify(this.activeWidgets));
        },

        _getDashboardManager() {
            const el = document.querySelector('[x-data="dashboardManager"]');
            if (!el) return null;
            return Alpine.$data(el);
        },

        _addToDashboard(widgetId) {
            const mgr = this._getDashboardManager();
            if (mgr && mgr.addWidget) {
                mgr.addWidget(widgetId);
            }
        },

        _removeFromDashboard(widgetId) {
            const mgr = this._getDashboardManager();
            if (!mgr || !mgr.grid) return;
            const items = mgr.grid.getGridItems();
            for (const item of items) {
                const gsId = item.getAttribute('gs-id') || item.gridstackNode?.id;
                if (gsId === widgetId) {
                    mgr.grid.removeWidget(item);
                    mgr.saveLayout();
                    break;
                }
            }
        }
    }));
});

// Exportar catálogo para uso en dashboard.js
window.ALL_WIDGETS_CATALOG = ALL_WIDGETS_CATALOG;
window.WIDGET_PANEL_KEY = WIDGET_PANEL_KEY;
