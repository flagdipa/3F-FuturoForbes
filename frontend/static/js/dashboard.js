/**
 * 3F Dashboard Manager
 * Handles GridStack lifecycle and widget state.
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('dashboardManager', () => ({
        grid: null,
        isEditing: false,
        availableWidgets: [
            { id: 'widget-balance-total', name: 'Balance Total', icon: 'fa-wallet', category: 'Financiero' },
            { id: 'widget-monthly-summary', name: 'Resumen Mensual', icon: 'fa-chart-bar', category: 'Financiero' },
            { id: 'widget-recent-transactions', name: 'Últimas Transacciones', icon: 'fa-list-ul', category: 'Financiero' },
            { id: 'widget-dolar-hoy', name: 'Dólar Hoy', icon: 'fa-dollar-sign', category: 'Plugins' },
            { id: 'widget-ia-insights', name: 'IA Insights', icon: 'fa-robot', category: 'IA' },
            { id: 'widget-quick-add', name: 'Acceso Rápido', icon: 'fa-plus-circle', category: 'Sistema' }
        ],
        activeWidgets: [],

        async init() {
            this.grid = GridStack.init({
                cellHeight: 70,
                margin: 8,
                float: false,
                column: 12,
                disableOneColumnMode: false,
                oneColumnModeDomSort: true,
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
            // Si hay un layout guardado de una versión anterior, descartarlo
            const LAYOUT_VERSION = 'v3';
            if (localStorage.getItem('3f_layout_version') !== LAYOUT_VERSION) {
                localStorage.removeItem('3f_dashboard_layout');
                localStorage.setItem('3f_layout_version', LAYOUT_VERSION);
            }
            try {
                let layout = null;
                try {
                    const response = await api.get('/auth/profile/dashboard-layout');
                    if (response.data && response.data.layout) {
                        layout = JSON.parse(response.data.layout);
                    }
                } catch (apiError) {
                    console.warn("Could not load layout from API, falling back to localStorage", apiError);
                    const saved = localStorage.getItem('3f_dashboard_layout');
                    if (saved) {
                        try { layout = JSON.parse(saved); } catch (e) { layout = null; }
                    }
                }

                // Validar que el layout tiene la forma correcta para GridStack v10
                if (layout && Array.isArray(layout) && layout.length > 0) {
                    const widgetIds = layout.map(item => item.id).filter(Boolean);
                    await this.loadRequiredWidgetScripts(widgetIds);
                    this.grid.load(layout);
                } else {
                    // Layout por defecto: 12 columnas sin huecos
                    // Respeta la seleccion del panel de checkboxes si existe
                    const panelSelection = (() => {
                        try {
                            const s = localStorage.getItem(window.WIDGET_PANEL_KEY || '3f_active_widgets');
                            return s ? JSON.parse(s) : null;
                        } catch(e) { return null; }
                    })();

                    const allDefault = [
                        { x: 0, y: 0, w: 4, h: 4, id: 'widget-balance-total' },
                        { x: 4, y: 0, w: 5, h: 6, id: 'widget-monthly-summary' },
                        { x: 9, y: 0, w: 3, h: 4, id: 'widget-dolar-hoy' },
                        { x: 0, y: 4, w: 7, h: 5, id: 'widget-recent-transactions' },
                        { x: 7, y: 4, w: 2, h: 5, id: 'widget-quick-add' },
                        { x: 9, y: 4, w: 3, h: 5, id: 'widget-ia-insights' }
                    ];

                    const defaultWidgetItems = panelSelection
                        ? allDefault.filter(w => panelSelection.includes(w.id))
                        : allDefault;

                    const defaultWidgets = defaultWidgetItems.map(w => w.id);
                    await this.loadRequiredWidgetScripts(defaultWidgets);
                    this.grid.load(defaultWidgetItems);
                }
            } catch (e) {
                console.error("Failed to load layout", e);
            }
        },

        async loadRequiredWidgetScripts(widgetIds) {
            const loadPromises = widgetIds.map(id => this.loadWidgetScript(id));
            await Promise.all(loadPromises);
        },

        async resetLayout() {
            if (confirm("¿Restaurar el diseño original del tablero? Perderás cualquier cambio de posición o widgets eliminados.")) {
                localStorage.removeItem('3f_dashboard_layout');
                try {
                    await api.delete('/auth/profile/dashboard-layout');
                } catch (e) { }
                window.location.reload();
            }
        },

        async saveLayout() {
            // Guardar SOLO posiciones e IDs, NO el contenido HTML.
            // Esto evita que GridStack restaure widgets con HTML viejo
            // que cause conflictos con la re-inyección de templates.
            const rawLayout = this.grid.save(false);
            const layout = rawLayout.map(item => ({
                id: item.id,
                x: item.x,
                y: item.y,
                w: item.w,
                h: item.h,
                minW: item.minW,
                minH: item.minH
            }));
            const layoutStr = JSON.stringify(layout);
            localStorage.setItem('3f_dashboard_layout', layoutStr);

            try {
                await api.post('/auth/profile/dashboard-layout', { layout: layoutStr });
            } catch (e) {
                console.warn("Failed to save layout to API", e);
            }
        },

        addWidget(widgetId) {
            // Implementado por override en index.html (post alpine:initialized)
            // Este método es un fallback si el override no está disponible
            this.loadWidgetScript(widgetId).then(() => {
                const tpl = document.getElementById('tpl-' + widgetId);
                const html = tpl ? tpl.innerHTML : `<div class="widget-header"><h5 class="widget-title">${widgetId}</h5></div>`;
                this.grid.addWidget({ w: 4, h: 3, id: widgetId, content: `<div class="grid-stack-item-content">${html}</div>` });
                this.saveLayout();
            });
        },

        async loadWidgetScript(widgetId) {
            const scriptSrc = `/static/js/widgets/${widgetId}.js`;
            if (!window.lazyLoader.loaded.has(scriptSrc)) {
                try {
                    await window.lazyLoader.loadScript(scriptSrc);
                } catch (e) {
                    console.warn(`Widget script not found: ${widgetId}`);
                }
            }
        },

        removeWidget(el) {
            this.grid.removeWidget(el);
            this.saveLayout();
        }
    }));
});
