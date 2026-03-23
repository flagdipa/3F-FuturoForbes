/**
 * Widget: Monthly Summary (Income vs Expense)
 * Compatible con carga dinámica (Alpine ya inicializado) y carga normal.
 */
(function registerWidgetMonthlySummary() {
    const def = () => ({
        loading: true,
        summary: { income: 0, expense: 0, budget: 0 },
        chart: null,

        init() {
            this.fetchData();
        },

        async fetchData() {
            this.loading = true;
            try {
                const now = new Date();
                const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1).toISOString().split('T')[0];
                const endOfMonth = new Date(now.getFullYear(), now.getMonth() + 1, 0).toISOString().split('T')[0];

                const res = await api.get(`/transactions/?limit=500&start_date=${startOfMonth}&end_date=${endOfMonth}&fecha_inicio=${startOfMonth}&fecha_fin=${endOfMonth}`);
                const txList = Array.isArray(res.data) ? res.data : (res.data?.data || []);

                let income = 0;
                let expense = 0;

                txList.forEach(tx => {
                    (tx.splits || []).forEach(split => {
                        const amt = parseFloat(split.amount);
                        if (amt > 0) income += amt;
                        else expense += Math.abs(amt);
                    });
                });

                // Dividir por 2 para evitar doble conteo en splits dobles
                this.summary = { income: income / 2, expense: expense / 2, budget: 0 };
                this.loading = false;
                this.$nextTick(() => this.initChart());
            } catch (e) {
                console.error("Monthly Summary Widget Error", e);
                this.loading = false;
            }
        },

        async initChart() {
            // Buscar canvas dentro del widget mismo usando la clase
            // (el template ahora usa class en lugar de id para evitar duplicados)
            let ctx = null;

            // Primero buscar dentro del stack de contexto de Alpine (el widget actual)
            if (this.$el) {
                ctx = this.$el.querySelector('canvas.chart-monthly-summary-canvas')
                    || this.$el.querySelector('canvas');
            }
            // Fallback: buscar por clase/id globalmente
            if (!ctx) {
                ctx = document.querySelector('canvas.chart-monthly-summary-canvas')
                    || document.getElementById('chart-monthly-summary');
            }
            if (!ctx) return;


            if (this.chart) this.chart.destroy();

            if (typeof Chart === 'undefined') {
                try {
                    await window.lazyLoader.loadChartJs();
                } catch (e) {
                    console.error('Failed to load Chart.js:', e);
                    return;
                }
            }

            this.chart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Ingresos', 'Gastos'],
                    datasets: [{
                        data: [this.summary.income, this.summary.expense],
                        backgroundColor: ['#00ff88', '#ff0055'],
                        borderWidth: 0,
                        hoverOffset: 10
                    }]
                },
                options: {
                    cutout: '80%',
                    plugins: {
                        legend: { display: false }
                    },
                    responsive: true,
                    maintainAspectRatio: false
                }
            });
        }
    });

    if (typeof Alpine !== 'undefined' && Alpine.data) {
        Alpine.data('widgetMonthlySummary', def);
    } else {
        document.addEventListener('alpine:init', () => Alpine.data('widgetMonthlySummary', def));
    }
})();
