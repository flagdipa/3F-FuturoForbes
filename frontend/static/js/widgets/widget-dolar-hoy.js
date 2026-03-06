/**
 * Widget: Dolar Hoy (Argentina)
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('widgetDolarHoy', () => ({
        loading: true,
        rates: {
            blue: { buy: 0, sell: 0 },
            oficial: { buy: 0, sell: 0 },
            mep: { price: 0 }
        },

        init() {
            this.fetchData();
        },

        async fetchData() {
            this.loading = true;
            try {
                // Mock data simulating DolarHoy plugin
                setTimeout(() => {
                    this.rates = {
                        blue: { buy: 1100, sell: 1120 },
                        oficial: { buy: 840, sell: 880 },
                        mep: { price: 1085.50 }
                    };
                    this.loading = false;
                }, 800);
            } catch (e) {
                console.error("DolarHoy Widget Error", e);
            }
        }
    }));
});
