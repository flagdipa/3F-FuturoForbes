/**
 * Sidebar Manager for 3F
 * Handles categorized account lists, investments, and assets.
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('sidebarManager', () => ({
        cuentas: [],
        investments: [],
        assets: [],
        loading: false,

        async init() {
            this.loading = true;
            try {
                // Fetch all data in parallel
                const [rCuentas, rInvestments, rAssets] = await Promise.all([
                    api.get('/cuentas/'),
                    api.get('/stocks/'),
                    api.get('/assets/')
                ]);

                this.cuentas = rCuentas.data.data || [];
                // Handle different response formats if necessary
                this.investments = rInvestments.data.data || rInvestments.data || [];
                this.assets = rAssets.data.data || rAssets.data || [];

            } catch (e) {
                console.error('SidebarManager Init Error:', e);
            } finally {
                this.loading = false;
            }
        },

        get filtered() {
            return {
                favoritas: this.cuentas.filter(c => c.cuenta_favorita === 1),
                bancarias: this.cuentas.filter(c => c.tipo_cuenta === 'Checking' || c.tipo_cuenta === 'Banco'),
                tarjetas: this.cuentas.filter(c => c.tipo_cuenta === 'Credit Card' || c.tipo_cuenta === 'Tarjeta'),
                efectivo: this.cuentas.filter(c => c.tipo_cuenta === 'Cash' || c.tipo_cuenta === 'Efectivo'),
                plazo: this.cuentas.filter(c => c.tipo_cuenta === 'Term' || c.tipo_cuenta === 'Plazo')
            };
        }
    }));
});
