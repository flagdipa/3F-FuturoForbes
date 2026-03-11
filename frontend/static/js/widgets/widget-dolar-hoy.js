/**
 * Widget: Dolar Hoy (Argentina)
 * Compatible con carga dinámica (Alpine ya inicializado) y carga normal.
 */
(function registerWidgetDolarHoy() {
    const def = () => ({
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
                // Intentar obtener datos reales del plugin
                const res = await api.get('/plugins/argentina-datos/dolar');
                if (res.data) {
                    this.rates = {
                        blue: { buy: res.data.blue?.buy || res.data.blue?.compra || 0, sell: res.data.blue?.sell || res.data.blue?.venta || 0 },
                        oficial: { buy: res.data.oficial?.buy || res.data.oficial?.compra || 0, sell: res.data.oficial?.sell || res.data.oficial?.venta || 0 },
                        mep: { price: res.data.mep?.price || res.data.bolsa?.venta || 0 }
                    };
                    this.loading = false;
                    return;
                }
            } catch (e) {
                // Plugin no disponible, usar mock
            }
            // Fallback: datos mock
            setTimeout(() => {
                this.rates = {
                    blue: { buy: 1100, sell: 1120 },
                    oficial: { buy: 840, sell: 880 },
                    mep: { price: 1085.50 }
                };
                this.loading = false;
            }, 800);
        }
    });

    if (typeof Alpine !== 'undefined' && Alpine.data) {
        Alpine.data('widgetDolarHoy', def);
    } else {
        document.addEventListener('alpine:init', () => Alpine.data('widgetDolarHoy', def));
    }
})();
