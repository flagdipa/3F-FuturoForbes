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
                    api.get('cuentas/'),
                    api.get('stocks/'),
                    api.get('assets/')
                ]);

                this.cuentas = rCuentas.data.data || [];
                // Handle different response formats if necessary
                this.investments = rInvestments.data.data || rInvestments.data || [];
                this.assets = rAssets.data.data || rAssets.data || [];

            } catch (e) {
                console.error('SidebarManager Init Error:', e);
            } finally {
                this.loading = false;
                this.highlightMenu();
            }
        },

        get filtered() {
            return {
                favoritas: this.cuentas.filter(c => c.cuenta_favorita === 1),
                bancarias: this.cuentas.filter(c => ['Checking', 'Banco', 'Savings', 'Caja de Ahorro'].includes(c.tipo_cuenta)),
                tarjetas: this.cuentas.filter(c => ['Credit Card', 'Tarjeta'].includes(c.tipo_cuenta)),
                efectivo: this.cuentas.filter(c => ['Cash', 'Efectivo'].includes(c.tipo_cuenta)),
                plazo: this.cuentas.filter(c => ['Term', 'Plazo', 'Inversion'].includes(c.tipo_cuenta))
            };
        },

        highlightMenu() {
            this.$nextTick(() => {
                const currentUrl = window.location.pathname + window.location.search;
                const links = document.querySelectorAll('.sidebar-menu a.nav-link');

                links.forEach(link => {
                    // Simple exact match or match base path for some cases
                    const href = link.getAttribute('href');
                    if (!href || href === '#') return;

                    // Check if current URL matches the link's href
                    // Use endsWith or includes depending on strictness needed
                    if (currentUrl === href || (href !== '/' && currentUrl.startsWith(href))) {
                        link.classList.add('active');

                        // Open parent menus
                        let parent = link.closest('.nav-treeview');
                        while (parent) {
                            parent.style.display = 'block'; // Force display for AdminLTE
                            const parentLi = parent.closest('.nav-item');
                            if (parentLi) {
                                parentLi.classList.add('menu-open');
                                const toggler = parentLi.querySelector('a.nav-link');
                                if (toggler) toggler.classList.add('active');
                            }
                            parent = parentLi ? parentLi.closest('.nav-treeview') : null;
                        }
                    }
                });
            });
        }
    }));
});
