/**
 * Widget: Recent Transactions
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('widgetRecentTransactions', () => ({
        loading: true,
        transactions: [],

        init() {
            this.fetchData();
        },

        async fetchData() {
            this.loading = true;
            try {
                // Mock data
                setTimeout(() => {
                    this.transactions = [
                        { id: 1, date: 'Hoy', desc: 'Súper Vea', amount: -15400.50, cat: 'Comida', type: 'EXPENSE' },
                        { id: 2, date: 'Ayer', desc: 'Sueldo IT', amount: 850000.00, cat: 'Salario', type: 'INCOME' },
                        { id: 3, date: '01 Mar', desc: 'Shell S.A.', amount: -22000.00, cat: 'Transporte', type: 'EXPENSE' },
                        { id: 4, date: '28 Feb', desc: 'Netflix', amount: -6500.00, cat: 'Ocio', type: 'EXPENSE' },
                        { id: 5, date: '27 Feb', desc: 'Transferencia InvertirOnline', amount: -50000.00, cat: 'Ahorro', type: 'TRANSFER' }
                    ];
                    this.loading = false;
                }, 600);
            } catch (e) {
                console.error("Recent Transactions Widget Error", e);
            }
        }
    }));
});
