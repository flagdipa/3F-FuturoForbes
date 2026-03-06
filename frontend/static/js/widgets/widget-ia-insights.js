/**
 * Widget: IA Insights
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('widgetIaInsights', () => ({
        loading: true,
        insights: [],

        init() {
            this.fetchData();
        },

        async fetchData() {
            this.loading = true;
            try {
                // Mock o fetch real
                // const res = await fetch('/api/v1/ia/insights');
                // this.insights = await res.json();

                setTimeout(() => {
                    this.insights = [
                        { type: "achievement", title: "Ahorro Sostenido", desc: "Tus gastos en transporte se redujeron 15% este mes." },
                        { type: "warning", title: "Alerta de Presupuesto", desc: "Estás a 10% de exceder el presupuesto de 'Salidas' y falta 1 semana para fin de mes." }
                    ];
                    this.loading = false;
                }, 1200);
            } catch (e) {
                console.error("Widget IA Insights Error", e);
            }
        }
    }));
});
