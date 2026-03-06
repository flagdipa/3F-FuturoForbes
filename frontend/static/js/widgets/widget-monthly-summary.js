/**
 * Widget: Monthly Summary (Income vs Expense)
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('widgetMonthlySummary', () => ({
        loading: true,
        summary: { income: 0, expense: 0, budget: 0 },
        chart: null,

        init() {
            this.fetchData();
        },

        async fetchData() {
            this.loading = true;
            try {
                // Mock data
                setTimeout(() => {
                    this.summary = { income: 950000, expense: 420000, budget: 500000 };
                    this.loading = false;
                    this.$nextTick(() => this.initChart());
                }, 1000);
            } catch (e) {
                console.error("Monthly Summary Widget Error", e);
            }
        },

        initChart() {
            const ctx = document.getElementById('chart-monthly-summary');
            if (!ctx) return;

            if (this.chart) this.chart.destroy();

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
    }));
});
