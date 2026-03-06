/**
 * 3F Dashboard Manager
 * Handles GridStack lifecycle and widget state.
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('dashboardManager', () => ({
        grid: null,
        isEditing: false,
        availableWidgets: [
            { id: 'widget-balance-total', name: 'Balance Total', icon: 'fa-wallet', category: 'Financial' },
            { id: 'widget-monthly-summary', name: 'Resumen Mensual', icon: 'fa-chart-bar', category: 'Financial' },
            { id: 'widget-recent-transactions', name: 'Últimas Transacciones', icon: 'fa-list-ul', category: 'Financial' },
            { id: 'widget-cashflow-chart', name: 'Flujo de Caja', icon: 'fa-chart-line', category: 'Financial' },
            { id: 'widget-dolar-hoy', name: 'Dólar Hoy', icon: 'fa-dollar-sign', category: 'Plugins' },
            { id: 'widget-ia-insights', name: 'IA Insights', icon: 'fa-robot', category: 'AI' },
            { id: 'widget-quick-add', name: 'Acceso Rápido', icon: 'fa-plus-circle', category: 'System' }
        ],
        activeWidgets: [],

        async init() {
            this.grid = GridStack.init({
                cellHeight: 80,
                margin: 10,
                float: true,
                draggable: { handle: '.widget-header', appendTo: 'body' },
                resizable: { handles: 'e, se, s, sw, w' }
            });

            this.grid.on('change', () => this.saveLayout());

            await this.loadLayout();
            this.setEditMode(false);
        },

        setEditMode(value) {
            this.isEditing = value;
            this.grid.setStatic(!value);
            if (value) {
                document.body.classList.add('dashboard-editing');
            } else {
                document.body.classList.remove('dashboard-editing');
            }
        },

        async loadLayout() {
            try {
                // In a real app, fetch from /api/v1/users/me/config/dashboard
                const saved = localStorage.getItem('3f_dashboard_layout');
                if (saved) {
                    const layout = JSON.parse(saved);
                    this.grid.load(layout);
                } else {
                    // Default layout
                    this.grid.load([
                        { x: 0, y: 0, w: 4, h: 2, id: 'widget-balance-total' },
                        { x: 4, y: 0, w: 4, h: 4, id: 'widget-monthly-summary' },
                        { x: 8, y: 0, w: 4, h: 2, id: 'widget-dolar-hoy' },
                        { x: 0, y: 2, w: 4, h: 4, id: 'widget-recent-transactions' }
                    ]);
                }
            } catch (e) {
                console.error("Failed to load layout", e);
            }
        },

        saveLayout() {
            const layout = this.grid.save(false);
            localStorage.setItem('3f_dashboard_layout', JSON.stringify(layout));
            // TODO: Post to API
        },

        addWidget(widgetId) {
            const widget = this.availableWidgets.find(w => w.id === widgetId);
            if (widget) {
                this.grid.addWidget({ w: 4, h: 2, id: widgetId, content: `<div class="widget-loader" data-widget="${widgetId}"></div>` });
                this.saveLayout();
            }
        },

        removeWidget(el) {
            this.grid.removeWidget(el);
            this.saveLayout();
        }
    }));
});
