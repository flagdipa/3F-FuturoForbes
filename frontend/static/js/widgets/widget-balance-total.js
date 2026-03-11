/**
 * Widget: Balance Total
 * Compatible con carga dinámica (Alpine ya inicializado) y carga normal.
 */
(function registerWidgetBalanceTotal() {
    const def = () => ({
        loading: true,
        total: 0,
        currency: 'ARS',
        history: [],

        init() {
            this.fetchData();
            setInterval(() => this.fetchData(), 300000);
        },

        async fetchData() {
            this.loading = true;
            try {
                const res = await api.get('/accounts/');
                const accounts = Array.isArray(res.data) ? res.data : (res.data?.data || []);
                this.total = accounts
                    .filter(a => a.type === 'ASSET' || a.type === 'asset')
                    .reduce((sum, a) => sum + parseFloat(a.current_balance || 0), 0);
                this.loading = false;
            } catch (e) {
                console.error("Balance Widget Error", e);
                this.loading = false;
            }
        }
    });

    if (typeof Alpine !== 'undefined' && Alpine.data) {
        Alpine.data('widgetBalanceTotal', def);
    } else {
        document.addEventListener('alpine:init', () => Alpine.data('widgetBalanceTotal', def));
    }
})();
