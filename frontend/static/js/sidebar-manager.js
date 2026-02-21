/**
 * Sidebar Manager for 3F
 * Handles categorized account lists, investments, and assets.
 */
document.addEventListener('alpine:init', () => {
    Alpine.data('sidebarManager', () => ({
        cuentas: [],
        investments: [],
        assets: [],
        activePlugins: [],
        argDatos: { blue: null, riesgo: null },
        loading: false,

        async init() {
            this.loading = true;
            try {
                const t = Date.now();
                // Fetch all data in parallel
                const [rCuentas, rInvestments, rAssets, rPlugins] = await Promise.all([
                    api.get(`cuentas/?t=${t}`),
                    api.get(`stocks/?t=${t}`),
                    api.get(`assets/?t=${t}`),
                    api.get('plugins/activos')
                ]);

                this.cuentas = rCuentas.data.data || [];
                this.investments = rInvestments.data.data || rInvestments.data || [];
                this.assets = rAssets.data.data || rAssets.data || [];
                this.activePlugins = rPlugins.data.plugins_cargados || [];

                // Fetch Argentina Datos mini if plugin is active
                if (this.isPluginActive('argentina_datos')) {
                    this.fetchArgDatosMini();
                }

            } catch (e) {
                console.error('SidebarManager Init Error:', e);
            } finally {
                this.loading = false;
                this.highlightMenu();
            }
        },

        async fetchArgDatosMini() {
            try {
                const res = await api.get('/config/plugins/argentina_datos/datos');
                const data = res.data;
                const blue = data['/v1/cotizaciones/dolares/blue']?.datos ||
                    data['/v1/cotizaciones']?.datos?.find(d => d.casa === 'blue');
                const riesgo = data['/v1/finanzas/indices/riesgo-pais/ultimo']?.datos;

                if (blue) this.argDatos.blue = blue.venta;
                if (riesgo) this.argDatos.riesgo = riesgo.valor;
            } catch (e) {
                console.warn('Error fetching Argentina Datos Mini:', e);
            }
        },

        isPluginActive(name) {
            return this.activePlugins.includes(name);
        },

        get filtered() {
            const activas = this.cuentas.filter(c => c.estado === 'Open');
            return {
                favoritas: activas.filter(c => c.cuenta_favorita === 1),
                bancarias: activas.filter(c => c.tipo_cuenta === 'Checking' || c.tipo_cuenta === 'Savings'),
                tarjetas: activas.filter(c => c.tipo_cuenta === 'Credit Card'),
                efectivo: activas.filter(c => c.tipo_cuenta === 'Cash'),
                plazo_fijo: activas.filter(c => c.tipo_cuenta === 'Term' || c.tipo_cuenta === 'Savings' && c.nombre_cuenta.toLowerCase().includes('ahorro')),
                otras: activas.filter(c => !['Checking', 'Savings', 'Credit Card', 'Cash', 'Term'].includes(c.tipo_cuenta)),
                // Currency-based views
                cuentas_ars: activas.filter(c => {
                    const iso = (c.divisa?.codigo_iso || '').toUpperCase().trim();
                    return iso === 'ARS' || iso === 'ARS$' || iso === '$';
                }),
                cuentas_usd: activas.filter(c => {
                    const iso = (c.divisa?.codigo_iso || '').toUpperCase().trim();
                    return iso === 'USD' || iso === 'U$S' || iso === 'USDT' || iso === 'U$D';
                }),
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
                            parent.style.display = 'block';
                            const parentLi = parent.closest('.nav-item');
                            if (parentLi) {
                                parentLi.classList.add('menu-open');
                                parentLi.classList.add('menu-is-open'); // Extra check for some LTE versions
                                const toggler = parentLi.querySelector(':scope > a.nav-link');
                                if (toggler) toggler.classList.add('active');
                            }
                            parent = parentLi ? parentLi.parentElement.closest('.nav-treeview') : null;
                        }
                    }
                });
            });
        }
    }));
});
