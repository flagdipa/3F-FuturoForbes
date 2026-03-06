/**
 * Widget: Balance Total
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('widgetBalanceTotal', () => ({
        loading: true,
        total: 0,
        currency: 'ARS',
        history: [],

        init() {
            this.fetchData();
            // Refresh every 5 minutes
            setInterval(() => this.fetchData(), 300000);
        },

        async fetchData() {
            this.loading = true;
            try {
                // Mocking API call
                // const res = await fetch('/api/v1/accounts/summary');
                // const data = await res.json();

                // Demo data
                setTimeout(() => {
                    this.total = 1250450.75;
                    this.loading = false;
                }, 500);
            } catch (e) {
                console.error("Balance Widget Error", e);
            }
        }
    }));
});
