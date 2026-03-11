/**
 * Widget: IA Insights
 * Compatible con carga dinámica (Alpine ya inicializado) y carga normal.
 */
(function registerWidgetIaInsights() {
    const def = () => ({
        loading: true,
        insights: [],

        init() {
            this.fetchData();
        },

        async fetchData() {
            this.loading = true;
            try {
                // Intentar endpoint real de IA
                const res = await api.get('/ia/insights');
                if (res.data && Array.isArray(res.data)) {
                    this.insights = res.data;
                    this.loading = false;
                    return;
                }
            } catch (e) {
                // Fallback a datos mock
            }

            setTimeout(() => {
                this.insights = [
                    { type: "achievement", title: "Ahorro Sostenido", desc: "Tus gastos en transporte se redujeron 15% este mes." },
                    { type: "warning", title: "Alerta de Presupuesto", desc: "Estás a 10% de exceder el presupuesto de 'Salidas' y falta 1 semana para fin de mes." }
                ];
                this.loading = false;
            }, 1200);
        }
    });

    if (typeof Alpine !== 'undefined' && Alpine.data) {
        Alpine.data('widgetIaInsights', def);
    } else {
        document.addEventListener('alpine:init', () => Alpine.data('widgetIaInsights', def));
    }
})();
