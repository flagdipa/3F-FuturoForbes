/**
 * Widget: Balance Total
 * Compatible con carga dinámica (Alpine ya inicializado) y carga normal.
 */
(function registerWidgetBalanceTotal() {
    const def = () => ({
        loading: true,
        total: 0,
        liquid: 0,
        investments: 0,
        currency: 'ARS',

        init() {
            this.fetchData();
            // Refresh every 5 minutes
            setInterval(() => this.fetchData(), 300000);
        },

        async fetchData() {
            this.loading = true;
            try {
                // Fetch basic data for consolidation
                const [rCuentas, rStocks, rAssets] = await Promise.all([
                    api.get('accounts/'),
                    api.get('investments/'),
                    api.get('assets/')
                ]);

                const accounts = Array.isArray(rCuentas.data) ? rCuentas.data : (rCuentas.data?.data || []);
                const stocks = Array.isArray(rStocks.data) ? rStocks.data : (rStocks.data?.data || []);
                const assets = Array.isArray(rAssets.data) ? rAssets.data : (rAssets.data?.data || []);

                // Calculate Liquid (Cash, Checking, Savings)
                this.liquid = accounts
                    .filter(a => ['Checking', 'Savings', 'Cash', 'ASSET'].includes(a.type))
                    .reduce((sum, a) => sum + parseFloat(a.current_balance || 0), 0);

                // Calculate Investments (Stocks + Real Estate Assets)
                const stocksValue = stocks.reduce((sum, s) => sum + parseFloat(s.current_value || s.market_value || s.amount || 0), 0);
                const assetsValue = assets.reduce((sum, a) => sum + parseFloat(a.current_valuation || a.current_value || a.purchase_price || 0), 0);
                
                this.investments = stocksValue + assetsValue;
                
                // Consolidate total
                this.total = this.liquid + this.investments;
                
                this.loading = false;
            } catch (e) {
                console.error("Balance Widget Consolidation Error:", e);
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
