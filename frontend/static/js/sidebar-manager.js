/**
 * Sidebar Manager for 3F
 * Handles dynamic menu structure, account grouping by type,
 * active plugins listing, and drag-and-drop reordering.
 * v3.0 - Dynamic + Sortable
 */
document.addEventListener('alpine:init', () => {
    Alpine.store('sidebar', {
        accounts: [],
        investments: [],
        assets: [],
        activePlugins: [],
        argDatos: { blue: null, riesgo: null },
        activeCurrency: 'ARS',
        loading: false,

        // Sidebar order state
        menuOrder: [],
        menuOrderLoaded: false,

        // Default order of sidebar items
        DEFAULT_ORDER: [
            'dashboard',
            'scheduled',
            'transactions_ars',
            'transactions_usd',
            'accounts_favoritas',
            'accounts_bancarias',
            'accounts_tarjeta',
            'accounts_billeteras',
            'accounts_efectivo',
            'accounts_plazo',
            'budgets',
            'goals',
            'modules',
            'reports',
            'vault',
            'settings',
        ],

        // Menu item definitions — maps key to label/icon/href
        MENU_ITEMS: {
            dashboard:           { labelKey: 'nav.dashboard',      icon: 'fa-solid fa-gauge-high',       iconColor: 'text-info',      href: '/dashboard' },
            scheduled:           { labelKey: 'nav.scheduled',       icon: 'fa-solid fa-calendar-check',   iconColor: 'text-warning',   href: '/programadas' },
            transactions_ars:    { labelKey: 'nav.trans_ars',       icon: 'fa-solid fa-money-bill-wave',  iconColor: 'text-success',   href: '/transacciones?currency=ARS' },
            transactions_usd:    { labelKey: 'nav.trans_usd',       icon: 'fa-solid fa-dollar-sign',      iconColor: 'text-cyan',      href: '/transacciones?currency=USD' },
            accounts_favoritas:  { labelKey: 'sidebar.acc_favoritas', icon: 'fa-solid fa-star',           iconColor: 'text-warning',   isAccountGroup: true, accountFilter: 'favoritas' },
            accounts_bancarias:  { labelKey: 'sidebar.acc_bancarias', icon: 'fa-solid fa-building-columns', iconColor: 'text-primary', isAccountGroup: true, accountFilter: 'bancarias' },
            accounts_tarjeta:    { labelKey: 'sidebar.acc_tarjeta',   icon: 'fa-solid fa-credit-card',    iconColor: 'text-danger',    isAccountGroup: true, accountFilter: 'tarjeta' },
            accounts_billeteras: { labelKey: 'sidebar.acc_billeteras', icon: 'fa-solid fa-mobile-screen', iconColor: 'text-purple',    isAccountGroup: true, accountFilter: 'billeteras' },
            accounts_efectivo:   { labelKey: 'sidebar.acc_efectivo',   icon: 'fa-solid fa-coins',         iconColor: 'text-success',   isAccountGroup: true, accountFilter: 'efectivo' },
            accounts_plazo:      { labelKey: 'sidebar.acc_plazo',      icon: 'fa-solid fa-clock',         iconColor: 'text-info',      isAccountGroup: true, accountFilter: 'plazo' },
            budgets:             { labelKey: 'nav.budgets',        icon: 'fa-solid fa-bullseye',         iconColor: 'text-warning',   href: '/presupuestos' },
            goals:               { labelKey: 'nav.goals',          icon: 'fa-solid fa-piggy-bank',       iconColor: 'text-warning',   href: '/metas' },
            modules:             { labelKey: 'sidebar.modules',    icon: 'fa-solid fa-puzzle-piece',     iconColor: 'text-purple',    isModules: true },
            reports:             { labelKey: 'nav.reports',         icon: 'fa-solid fa-chart-pie',        iconColor: 'text-cyan',      href: '/reportes',
                                   children: [
                                       { labelKey: 'nav.reports_cashflow', href: '/reportes/cashflow' },
                                       { labelKey: 'nav.reports_heatmap', href: '/reportes/heatmap' },
                                   ]},
            vault:               { labelKey: 'nav.vault',          icon: 'fa-solid fa-vault',            iconColor: 'text-info',      href: '/vault' },
            settings:            { labelKey: 'nav.settings',       icon: 'fa-solid fa-sliders',          iconColor: 'text-secondary', href: '/configuracion' },
        },

        // Account type classification rules
        ACCOUNT_CLASSIFY_RULES: {
            bancarias: {
                namePatterns: ['banco', 'bank', 'galicia', 'santander', 'bbva', 'macro', 'nacion', 'brubank', 'wilobank', 'hsbc', 'icbc', 'itau', 'supervielle', 'patagonia', 'comafi', 'bind', 'hipotecario', 'columbia', 'citi'],
                institutionTypes: ['bank', 'banco'],
            },
            tarjeta: {
                namePatterns: ['tarjeta', 'visa', 'mastercard', 'amex', 'credit card', 'credito', 'crédito', 'tc '],
                accountNotes: ['credit_card'],
            },
            billeteras: {
                namePatterns: ['mercadopago', 'mp ', 'uala', 'ualá', 'prex', 'bimo', 'modo', 'naranja x', 'personal pay', 'yacare', 'todopago', 'paypal', 'skrill', 'wallet', 'billetera'],
                institutionTypes: ['wallet', 'billetera', 'fintech'],
            },
            efectivo: {
                namePatterns: ['efectivo', 'cash', 'caja', 'bolsillo'],
            },
            plazo: {
                namePatterns: ['plazo fijo', 'plazo', 'term', 'fixed deposit', 'fci', 'fondo'],
            },
        },

        syncCurrency() {
            const params = new URLSearchParams(window.location.search);
            this.activeCurrency = (params.get('currency') || 'ARS').toUpperCase();
        },

        async init() {
            this.syncCurrency();
            window.addEventListener('popstate', () => this.syncCurrency());
            this.loading = true;
            try {
                const t = Date.now();
                const [rAccounts, rInvestments, rAssets, rPlugins, rPrefs] = await Promise.all([
                    api.get(`accounts/?t=${t}`),
                    api.get(`investments/?t=${t}`),
                    api.get(`assets/?t=${t}`),
                    api.get('plugins/activos'),
                    api.get('users/me/ui-preferences').catch(() => ({ data: { sidebar_order: null } })),
                ]);

                // Normalización Robusta de Cuentas
                this.accounts = (rAccounts.data?.data || rAccounts.data || []).map(c => ({
                    ...c,
                    id: c.id || c.id_cuenta,
                    name: c.name || c.nombre_cuenta || 'S/N',
                    currency_code: c.currency_code || c.moneda || 'ARS',
                    type: c.type || c.tipo_cuenta || 'ASSET',
                    is_active: c.is_active === true || c.activo === 1,
                    balance: parseFloat(c.balance || c.saldo || c.current_balance || 0),
                    _lowerName: (c.name || c.nombre_cuenta || '').toLowerCase(),
                }));

                this.investments = (rInvestments.data?.data || rInvestments.data || []).map(i => ({
                    ...i,
                    id: i.id || i.id_stock
                }));

                this.assets = (rAssets.data?.data || rAssets.data || []).map(a => ({
                    ...a,
                    id: a.id || a.id_asset
                }));

                this.activePlugins = rPlugins.data?.plugins_cargados || [];

                // Load sidebar order preferences
                const savedOrder = rPrefs.data?.sidebar_order;
                if (savedOrder && Array.isArray(savedOrder) && savedOrder.length > 0) {
                    // Merge: keep saved order but add any new items that didn't exist before
                    const newItems = this.DEFAULT_ORDER.filter(k => !savedOrder.includes(k));
                    // Also add dynamic account groups that have accounts
                    this.menuOrder = [...savedOrder, ...newItems];
                } else {
                    this.menuOrder = [...this.DEFAULT_ORDER];
                }
                // Add any dynamic account type groups not yet in menuOrder
                this._addDynamicAccountGroups();
                this.menuOrderLoaded = true;

                if (this.isPluginActive('argentina_datos')) {
                    this.fetchArgDatosMini();
                }

            } catch (e) {
                console.error('Sidebar Store Init Error:', e);
                this.menuOrder = [...this.DEFAULT_ORDER];
                this.menuOrderLoaded = true;
            } finally {
                this.loading = false;
                Alpine.nextTick(() => {
                    this.highlightMenu();
                    this._initSortable();
                });
            }
        },

        /**
         * Check for account types that exist but don't have a menu key yet.
         * This handles the requirement: "A medida que se crean mas tipo de cuentas
         * que aparezcan como nuevos item"
         */
        _addDynamicAccountGroups() {
            const activeAccounts = (this.accounts || []).filter(c => c.is_active);
            const grouped = this._classifyAccounts(activeAccounts);
            // For each group with accounts, ensure there's a menu key
            for (const [groupKey, accs] of Object.entries(grouped)) {
                const menuKey = `accounts_${groupKey}`;
                if (accs.length > 0 && !this.menuOrder.includes(menuKey)) {
                    // Insert before 'budgets' if exists, otherwise at end
                    const budgetIdx = this.menuOrder.indexOf('budgets');
                    if (budgetIdx !== -1) {
                        this.menuOrder.splice(budgetIdx, 0, menuKey);
                    } else {
                        this.menuOrder.push(menuKey);
                    }
                    // Also add a dynamic MENU_ITEMS entry
                    if (!this.MENU_ITEMS[menuKey]) {
                        this.MENU_ITEMS[menuKey] = {
                            labelKey: `sidebar.acc_${groupKey}`,
                            icon: 'fa-solid fa-wallet',
                            iconColor: 'text-muted',
                            isAccountGroup: true,
                            accountFilter: groupKey,
                        };
                    }
                }
            }
        },

        /**
         * Classify accounts into groups based on name patterns and metadata.
         */
        _classifyAccounts(accounts) {
            const result = {
                favoritas: [],
                bancarias: [],
                tarjeta: [],
                billeteras: [],
                efectivo: [],
                plazo: [],
                _otros: [],
            };

            for (const acc of accounts) {
                const name = acc._lowerName || (acc.name || '').toLowerCase();
                const notes = (acc.notes || '').toLowerCase();
                let classified = false;

                for (const [group, rules] of Object.entries(this.ACCOUNT_CLASSIFY_RULES)) {
                    const matchesName = (rules.namePatterns || []).some(p => name.includes(p));
                    const matchesNotes = (rules.accountNotes || []).some(p => notes.includes(p));
                    if (matchesName || matchesNotes) {
                        result[group] = result[group] || [];
                        result[group].push(acc);
                        classified = true;
                        break;
                    }
                }
                if (!classified) {
                    result._otros.push(acc);
                }
            }
            return result;
        },

        /**
         * Get the accounts for a specific group, filtered by active currency.
         */
        getAccountsForGroup(filterKey) {
            const activeAccounts = (this.accounts || []).filter(c => c.is_active);
            const getIso = (c) => (c.currency_code || '').toUpperCase().trim();
            const currencyAccounts = activeAccounts.filter(c => {
                if (this.activeCurrency === 'ARS') {
                    return ['ARS', 'ARS$', '$'].includes(getIso(c));
                }
                return ['USD', 'U$S', 'USDT', 'U$D'].includes(getIso(c));
            });

            if (filterKey === 'favoritas') {
                // Favoritas: accounts marked via notes or custom field
                return currencyAccounts.filter(c => (c.notes || '').toLowerCase().includes('favorita') || (c.notes || '').toLowerCase().includes('favorite'));
            }

            const classified = this._classifyAccounts(currencyAccounts);
            return classified[filterKey] || [];
        },

        /**
         * Get items for the menu, ordered by user preference.
         */
        get orderedMenu() {
            if (!this.menuOrderLoaded) return [];
            return this.menuOrder
                .filter(key => {
                    const def = this.MENU_ITEMS[key];
                    if (!def) return false;
                    // Hide account groups with no accounts
                    if (def.isAccountGroup) {
                        return this.getAccountsForGroup(def.accountFilter).length > 0;
                    }
                    // Hide modules if no active plugins
                    if (def.isModules) {
                        return true; // Always show modules section as entry point
                    }
                    return true;
                })
                .map(key => ({ key, ...this.MENU_ITEMS[key] }));
        },

        // Keep legacy filtered getter for backward compat
        get filtered() {
            const activas = (this.accounts || []).filter(c => c.is_active);
            const getIso = (c) => (c.currency_code || '').toUpperCase().trim();
            return {
                cuentas_ars: activas.filter(c => ['ARS', 'ARS$', '$'].includes(getIso(c))),
                cuentas_usd: activas.filter(c => ['USD', 'U$S', 'USDT', 'U$D'].includes(getIso(c)))
            };
        },

        /**
         * Initialize SortableJS on the sidebar menu list.
         */
        _initSortable() {
            const el = document.getElementById('sidebar-sortable-list');
            if (!el || typeof Sortable === 'undefined') return;

            this._sortableInstance = Sortable.create(el, {
                animation: 150,
                handle: '.sidebar-drag-handle',
                ghostClass: 'sidebar-sortable-ghost',
                chosenClass: 'sidebar-sortable-chosen',
                dragClass: 'sidebar-sortable-drag',
                filter: '.sidebar-no-drag',
                onEnd: (evt) => {
                    // Rebuild menuOrder from DOM
                    const items = el.querySelectorAll('[data-menu-key]');
                    const newOrder = Array.from(items).map(i => i.dataset.menuKey);
                    this.menuOrder = newOrder;
                    this._savePreferences(newOrder);
                },
            });
        },

        /**
         * Persist sidebar order to backend.
         */
        async _savePreferences(order) {
            try {
                await api.put('users/me/ui-preferences', { sidebar_order: order });
            } catch (e) {
                console.warn('Could not save sidebar preferences:', e);
            }
        },

        async fetchArgDatosMini() {
            try {
                const res = await api.get('/config/plugins/argentina_datos/datos');
                const data = res.data;
                const blue = data['/api/cotizaciones/dolares/blue']?.datos ||
                    data['/api/cotizaciones']?.datos?.find(d => d.casa === 'blue');
                const riesgo = data['/api/finanzas/indices/riesgo-pais/ultimo']?.datos;
                if (blue) this.argDatos.blue = Math.round(blue.venta);
                if (riesgo) this.argDatos.riesgo = Math.round(riesgo.valor);
            } catch (e) {
                console.warn('Error fetching Argentina Datos Mini:', e);
            }
        },

        isPluginActive(name) {
            return (this.activePlugins || []).includes(name);
        },

        selectAccountForFiltering(id) {
            if (window.location.pathname.includes('/transacciones')) {
                window.dispatchEvent(new CustomEvent('sidebar-account-selected', { detail: { id } }));
            } else {
                window.location.href = `/transacciones?account_id=${id}&currency=${this.activeCurrency}`;
            }
        },

        highlightMenu() {
            Alpine.nextTick(() => {
                const currentUrl = window.location.pathname + window.location.search;
                const links = document.querySelectorAll('.sidebar-menu a.nav-link');
                links.forEach(link => {
                    const href = link.getAttribute('href');
                    if (!href || href === '#') return;
                    if (currentUrl === href || (href !== '/' && currentUrl.startsWith(href))) {
                        link.classList.add('active');
                        let parent = link.closest('.nav-treeview');
                        while (parent) {
                            parent.style.display = 'block';
                            const parentLi = parent.closest('.nav-item');
                            if (parentLi) {
                                parentLi.classList.add('menu-open');
                                const toggler = parentLi.querySelector(':scope > a.nav-link');
                                if (toggler) toggler.classList.add('active');
                            }
                            parent = parentLi ? parentLi.parentElement.closest('.nav-treeview') : null;
                        }
                    }
                });
            });
        },

        /**
         * Get a translation with fallback
         */
        t(key) {
            try { return Alpine.store('lang')?.t(key) || key; } catch { return key; }
        }
    });

    // Auto-init store
    Alpine.store('sidebar').init();
});
