/**
 * Widget: Recent Transactions
 * Compatible con carga dinámica (Alpine ya inicializado) y carga normal.
 */
(function registerWidgetRecentTransactions() {
    const def = () => ({
        loading: true,
        transactions: [],

        init() {
            this.fetchData();
        },

        async fetchData() {
            this.loading = true;
            try {
                const response = await api.get('/transactions/?limit=5&sort_by=date&order=desc');
                const rawList = Array.isArray(response.data) ? response.data : (response.data.data || []);

                this.transactions = rawList.map(tx => {
                    let amount = 0;
                    let type = "UNKNOWN";
                    if (tx.splits && tx.splits.length > 0) {
                        amount = parseFloat(tx.splits[0].amount);
                        type = amount > 0 ? "INCOME" : "EXPENSE";
                        if (tx.splits.length === 2 && parseFloat(tx.splits[0].amount) === -parseFloat(tx.splits[1].amount)) {
                            type = "TRANSFER";
                            amount = Math.abs(amount);
                        }
                    }

                    return {
                        id: tx.id,
                        date: new Date(tx.date).toLocaleDateString('es-AR'),
                        desc: tx.description || tx.notes || 'Transacción',
                        amount: amount,
                        type: type
                    };
                });

                this.loading = false;
            } catch (e) {
                console.error("Recent Transactions Widget Error", e);
                this.loading = false;
            }
        }
    });

    if (typeof Alpine !== 'undefined' && Alpine.data) {
        Alpine.data('widgetRecentTransactions', def);
    } else {
        document.addEventListener('alpine:init', () => Alpine.data('widgetRecentTransactions', def));
    }
})();
