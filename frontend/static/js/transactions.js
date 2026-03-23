function initTransactionsComponent() {
        if (!window.Alpine) return;
        Alpine.data('transaccionesPage', () => ({
            transactions: [],
            selectedTxId: null,
            offset: 0,
            limit: 100,
            loading: false,
            hasMore: true,
            attachments: [],
            editTx: { tags: [], splits: [], is_split: false },
            bsModal: null,
            saving: false,
            isScanningReceipt: false,
            allTags: [],
            filters: {
                search: '',
                start_date: '',
                end_date: '',
                account_id: '',
                payee_id: '',
                category_id: '',
                tag_id: '',
                currency: ''
            },
            collections: {
                accounts: [],
                payees: [],
                categories: []
            },
            
            defaultColumns: [
                { key: 'tipo', class: 'border-primary' },
                { key: 'fecha', class: 'col-md-1 d-none d-md-table-cell border-primary' },
                { key: 'hora', class: 'd-none d-lg-table-cell border-primary' },
                { key: 'cuenta', class: 'col-md-2 border-primary text-truncate' },
                { key: 'beneficiario', class: 'col-md-3 border-primary text-truncate' },
                { key: 'categoria', class: 'col-md-2 d-none d-sm-table-cell border-primary text-truncate' },
                { key: 'monto', class: 'col-md-1 border-primary', align: 'end' },
                { key: 'saldo', class: 'col-md-1 d-none d-lg-table-cell border-primary', align: 'end' },
                { key: 'etiquetas', class: 'd-none d-xl-table-cell border-primary' },
                { key: 'estado', class: 'd-none d-md-table-cell border-primary' }
            ],
            columns: [],
            sortable: null,
            sortCol: 'fecha',
            sortAsc: false, // Default desc order (newest first)

            async init() {
                // Load columns from localStorage if available
                const savedOrder = localStorage.getItem('tx_columns_order_v1');
                if (savedOrder) {
                    const orderKeys = JSON.parse(savedOrder);
                    this.columns = orderKeys.map(k => this.defaultColumns.find(c => c.key === k)).filter(Boolean);
                    // Add any new columns that might have been added since save
                    this.defaultColumns.forEach(c => {
                        if (!this.columns.find(saved => saved.key === c.key)) {
                            this.columns.push(c);
                        }
                    });
                } else {
                    this.columns = [...this.defaultColumns];
                }
                
                let attempts = 0;
                while (typeof bootstrap === 'undefined' && attempts < 20) {
                    await new Promise(r => setTimeout(r, 100));
                    attempts++;
                }
                if (typeof bootstrap !== 'undefined') {
                    const modalEl = document.getElementById('modalNuevo');
                    if (modalEl) this.bsModal = new bootstrap.Modal(modalEl);
                }

                // --- Handle Account/Currency Filtering from Navigation ---
                const urlParams = new URLSearchParams(window.location.search);
                if (urlParams.has('account_id') || urlParams.has('id_cuenta')) {
                    this.filters.account_id = urlParams.get('account_id') || urlParams.get('id_cuenta');
                }
                if (urlParams.has('currency')) {
                    this.filters.currency = urlParams.get('currency');
                }

                await this.loadCollections();
                await this.loadMore();
                
                // --- Listen for sidebar account selection (smooth filtering) ---
                window.addEventListener('sidebar-account-selected', (e) => {
                    this.filters.account_id = e.detail.id;
                    this.applyFilters();
                });

                // Initialize Sortable and Resizers after data load and DOM update
                this.$nextTick(() => {
                    this.initSortable();
                    this.initColumnResizers();
                });
            },

            initColumnResizers() {
                const headers = document.querySelectorAll('#tx-headers th');
                headers.forEach(th => {
                    if (th.querySelector('.resizer')) return;

                    const resizer = document.createElement('div');
                    resizer.classList.add('resizer');
                    th.appendChild(resizer);

                    let x = 0;
                    let w = 0;

                    const mouseMoveHandler = (e) => {
                        const dx = e.clientX - x;
                        th.style.width = `${w + dx}px`;
                        th.classList.add('resizing'); // Optional style hook
                        resizer.classList.add('resizing');
                    };

                    const mouseUpHandler = () => {
                        document.removeEventListener('mousemove', mouseMoveHandler);
                        document.removeEventListener('mouseup', mouseUpHandler);
                        th.classList.remove('resizing');
                        resizer.classList.remove('resizing');
                    };

                    const mouseDownHandler = (e) => {
                        x = e.clientX;
                        const styles = window.getComputedStyle(th);
                        w = parseInt(styles.width, 10);

                        document.addEventListener('mousemove', mouseMoveHandler);
                        document.addEventListener('mouseup', mouseUpHandler);
                        e.stopPropagation(); // Prevent sorting trigger
                        e.preventDefault();
                    };

                    resizer.addEventListener('mousedown', mouseDownHandler);
                    // Prevent sort click on resizer
                    resizer.addEventListener('click', e => e.stopPropagation());
                });
            },

            initSortable() {
                const el = document.getElementById('tx-headers');
                if (!el) return;
                
                this.sortable = new Sortable(el, {
                    animation: 150,
                    ghostClass: 'bg-primary',
                    handle: 'th',
                    onStart: (evt) => {
                        // Store original order before drag
                        this._preDragColumns = [...this.columns];
                    },
                    onEnd: (evt) => {
                        // Revert DOM manipulation done by Sortable (Alpine manages DOM)
                        const parent = evt.from;
                        const movedEl = evt.item;
                        if (evt.oldIndex < evt.newIndex) {
                            parent.insertBefore(movedEl, parent.children[evt.oldIndex]);
                        } else {
                            parent.insertBefore(movedEl, parent.children[evt.oldIndex + 1]);
                        }

                        // Now update the data array (Alpine will re-render)
                        const cols = [...this._preDragColumns];
                        const item = cols.splice(evt.oldIndex, 1)[0];
                        cols.splice(evt.newIndex, 0, item);
                        this.columns = cols;

                        // Save Order
                        const keys = this.columns.map(c => c.key);
                        localStorage.setItem('tx_columns_order_v1', JSON.stringify(keys));
                    }
                });
            },

            sortBy(key) {
                if (this.sortCol === key) {
                    this.sortAsc = !this.sortAsc;
                } else {
                    this.sortCol = key;
                    this.sortAsc = true;
                }
                // Reset pagination and reload
                this.applyFilters();
            },

            async loadCollections() {
                try {
                    const unwrap = r => Array.isArray(r.data) ? r.data : (r.data?.data || []);
                    const [tags, accounts, payees, categories] = await Promise.all([
                        api.get('/tags/'),
                        api.get('/accounts/'),
                        api.get('/payees/'),
                        api.get('/categories/')
                    ]);
                    this.allTags = unwrap(tags).map(t => ({
                        ...t,
                        id: t.id ?? t.id_etiqueta,
                        name: t.name ?? t.nombre_etiqueta
                    }));
                    this.collections.accounts = unwrap(accounts).map(c => ({
                        ...c,
                        id: c.id ?? c.id_cuenta,
                        name: c.name ?? c.nombre_cuenta
                    }));
                    this.collections.payees = unwrap(payees).map(b => ({
                        ...b,
                        id: b.id ?? b.id_beneficiario,
                        name: b.name ?? b.nombre_beneficiario
                    }));
                    this.collections.categories = unwrap(categories).map(c => ({
                        ...c,
                        id: c.id ?? c.id_categoria,
                        name: c.name ?? c.nombre_categoria
                    }));
                } catch (e) { console.error('Error loading collections:', e); }
            },

            async loadMore() {
                if (this.loading || !this.hasMore) return;
                this.loading = true;
                try {
                    const params = {
                        skip: this.offset,
                        limit: this.limit
                    };

                    // Map sort column
                    const sortMap = { 
                        'fecha': 'date', 
                        'beneficiario': 'payee', 
                        'monto': 'amount', 
                        'cuenta': 'account', 
                        'categoria': 'category' 
                    };
                    params.sort_by = sortMap[this.sortCol] || 'date';
                    params.order = this.sortAsc ? 'asc' : 'desc';

                    // Apply filters
                    if (this.filters.account_id) params.account_id = this.filters.account_id;
                    if (this.filters.payee_id) params.payee_id = this.filters.payee_id;
                    if (this.filters.category_id) params.category_id = this.filters.category_id;
                    if (this.filters.start_date) params.start_date = this.filters.start_date;
                    if (this.filters.end_date) params.end_date = this.filters.end_date;
                    if (this.filters.search) params.description = this.filters.search;
                    if (this.filters.currency) params.currency = this.filters.currency;

                    const res = await api.get('/transactions/', { params });
                    const unwrap = r => Array.isArray(r.data) ? r.data : (r.data?.data || []);
                    const data = unwrap(res);
                    
                    this.hasMore = (data.length >= this.limit);

                    // Calculation of Running Balance if filtered by account
                    let runningBalance = null;
                    if (this.filters.account_id) {
                        const cta = this.collections.accounts.find(c => c.id == this.filters.account_id);
                        if (cta) {
                            // If first load and newest first, start with current account balance
                            if (this.offset === 0 && !this.sortAsc) {
                                runningBalance = parseFloat(cta.saldo_actual || cta.balance);
                            } else if (this.transactions.length > 0) {
                                // Continue from the balance of the last row
                                const lastTx = this.transactions[this.transactions.length - 1];
                                if (lastTx.balance !== null) {
                                    runningBalance = parseFloat(lastTx.balance) - parseFloat(lastTx.amount);
                                }
                            }
                        }
                    }

                    const nuevas = data.map(tx => {
                        const row = this.formatDataFromV2(tx);
                        if (runningBalance !== null) {
                            row.balance = runningBalance;
                            // Subtract the current transaction amount to get the balance BEFORE it
                            runningBalance = parseFloat(runningBalance) - parseFloat(row.amount);
                        }
                        return row;
                    });
                    
                    this.transactions = [...this.transactions, ...nuevas];
                    this.offset += data.length;
                } catch (error) {
                    console.error('Error al cargar transacciones:', error);
                } finally {
                    this.loading = false;
                }
            },
            
            handleScroll(e) {
                const { scrollTop, scrollHeight, clientHeight } = e.target;
                if (scrollTop + clientHeight >= scrollHeight - 50) this.loadMore();
            },
            
            formatCurrency(v) { return CurrencyUtils.formatCurrency(v); },
            formatFechaOnly(f) { return f ? new Date(f).toLocaleDateString() : '-'; },
            formatHoraOnly(f) { return f ? new Date(f).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '-'; },
            
            applyFilters() {
                this.transactions = [];
                this.offset = 0;
                this.hasMore = true;
                this.loadMore();
            },

            clearFilters() {
                this.filters = {
                    search: '',
                    start_date: '',
                    end_date: '',
                    account_id: '',
                    payee_id: '',
                    category_id: '',
                    tag_id: '',
                    currency: ''
                };
                this.applyFilters();
            },
            
            getAccountName(id) {
                let acc = this.collections.accounts.find(c => c.id == id);
                return acc ? acc.name : 'Account #' + id;
            },
            
            getCategoryName(id) {
                if (!id) return null;
                let c = this.collections.categories.find(c => c.id == id);
                return c ? c.name : 'Cat #' + id;
            },
            
            getPayeeName(id) {
                if (!id) return null;
                let b = this.collections.payees.find(b => b.id == id);
                return b ? b.name : 'Ben #' + id;
            },
                      formatDataFromV2(tx) {
                // Determine the primary account and category from the first split
                const primarySplit = tx.splits && tx.splits.length > 0 ? tx.splits[0] : {};
                const accountId = primarySplit.account_id;
                const categoryId = primarySplit.category_id;
                const isExpense = (primarySplit.amount || 0) < 0;

                let mainRow = {
                    id: tx.id, // Primary key for Alpine x-for
                    date: tx.date,
                    description: tx.description || 'Sin descripción',
                    payee_name: tx.payee ? tx.payee.name : (this.getPayeeName(tx.payee_id) || 'Varios'),
                    account_name: this.getAccountName(accountId) || 'N/A',
                    category_name: this.getCategoryName(categoryId) || 'N/A',
                    amount: primarySplit.amount || 0,
                    balance: tx.balance ?? null,
                    status: tx.status,
                    tags: tx.tags ? tx.tags.map(t => t.name) : [],
                    // Additional fields for editing/filtering
                    payee_id: tx.payee_id,
                    account_id: accountId,
                    category_id: categoryId,
                    notes: tx.notes || tx.description || '',
                    is_split: false
                };

                let splits = tx.splits || [];
                let isTransfer = false;
                
                // Transfer detection: 2 splits, different accounts, sum zero
                if (splits.length === 2) {
                    const s1 = splits[0], s2 = splits[1];
                    const sum = parseFloat(s1.amount) + parseFloat(s2.amount);
                    if (Math.abs(sum) < 0.001 && s1.account_id !== s2.account_id) isTransfer = true;
                }

                if (isTransfer) {
                    mainRow.transaction_code = 'Transfer';
                    let fromSplit = splits.find(s => parseFloat(s.amount) < 0);
                    let toSplit   = splits.find(s => parseFloat(s.amount) > 0);
                    mainRow.amount = Math.abs(parseFloat(fromSplit?.amount || splits[0].amount));
                    mainRow.account_id = fromSplit?.account_id;
                    mainRow.target_account_id = toSplit?.account_id;
                    mainRow.account_name = `${this.getAccountName(fromSplit?.account_id)} → ${this.getAccountName(toSplit?.account_id)}`;
                    mainRow.category_name = 'Transferencia';
                    mainRow.balance = null;
                } else if (splits.length === 0) {
                    mainRow.transaction_code = 'Unknown';
                    mainRow.amount = 0;
                    mainRow.account_name = '-';
                    mainRow.category_name = '-';
                    mainRow.balance = null;
                } else if (splits.length === 1) {
                    let amount = parseFloat(splits[0].amount);
                    mainRow.transaction_code = amount >= 0 ? 'Deposit' : 'Withdrawal';
                    mainRow.amount = Math.abs(amount);
                    mainRow.account_id = splits[0].account_id;
                    mainRow.category_id = splits[0].category_id;
                    mainRow.account_name = this.getAccountName(splits[0].account_id);
                    mainRow.category_name = this.getCategoryName(splits[0].category_id);
                    mainRow.balance = null;
                } else {
                    // Multiple splits — split transaction or single-entry categorization
                    mainRow.is_split = splits.length > 1;
                    
                    // The total transaction amount for a non-transfer is the absolute sum of all splits 
                    // (since they all point to the same account in single-entry mode)
                    const totalAmt = splits.reduce((sum, s) => sum + parseFloat(s.amount), 0);
                    mainRow.transaction_code = totalAmt >= 0 ? 'Deposit' : 'Withdrawal';
                    mainRow.amount = Math.abs(totalAmt);
                    
                    mainRow.account_id = splits[0].account_id;
                    mainRow.category_id = splits[0].category_id;
                    mainRow.account_name = this.getAccountName(splits[0].account_id);
                    
                    if (splits.length === 1) {
                        mainRow.category_name = this.getCategoryName(splits[0].category_id);
                    } else {
                        mainRow.category_name = 'Dividida (' + splits.length + ' divs)';
                    }
                    mainRow.balance = null;
                    
                    // Store divisiones for editing
                    mainRow.splits = splits.map(s => ({
                        category_id: s.category_id,
                        amount: Math.abs(parseFloat(s.amount)),
                        notes: s.memo || ''
                    }));
                }
                return mainRow;
            },

            newTransaction() {
                this.editTx = {
                    id: 'NEW',
                    date: new Date().toISOString().slice(0, 16),
                    amount: null,
                    account_id: this.collections.accounts[0]?.id || null,
                    payee_id: this.collections.payees[0]?.id || null,
                    category_id: null,
                    target_account_id: null,
                    transaction_code: 'Withdrawal',
                    tags: [],
                    splits: [],
                    is_split: false,
                    notes: '',
                    status: 'PENDING'
                };
                this.attachments = [];
                if (this.bsModal) this.bsModal.show();
            },

            async editTransaction(txOrId) {
                let tx = typeof txOrId === 'object' ? txOrId : this.transactions.find(t => t.id === txOrId);
                if (!tx) {
                    try {
                        const res = await api.get(`/transactions/${txOrId}`);
                        tx = this.formatDataFromV2(res.data);
                    } catch (e) {
                         console.error('Error loading transaction by ID:', txOrId);
                         return;
                    }
                }
                this.selectedTxId = tx.id;
                // Copia profunda
                this.editTx = JSON.parse(JSON.stringify(tx));
                if (!this.editTx.tags) this.editTx.tags = [];
                if (!this.editTx.splits) this.editTx.splits = [];
                this.attachments = [];
                
                if (this.editTx.date) {
                    try {
                        this.editTx.date = new Date(this.editTx.date).toISOString().slice(0, 16);
                    } catch(e) {}
                }

                // Cargar divisiones si es una TX dividida
                if (this.editTx.is_split) {
                    if (!this.editTx.splits || this.editTx.splits.length === 0) {
                        try {
                            const res = await api.get(`/transactions/${tx.id}`);
                            // Map V2 splits format to form divisiones format
                            this.editTx.splits = (res.data.splits || []).map(s => ({
                                category_id: s.category_id,
                                amount: Math.abs(parseFloat(s.amount)),
                                notes: s.memo || ''
                            }));
                        } catch (e) {
                            console.error('Error loading splits:', e);
                        }
                    }
                }

                // Cargar adjuntos
                await this.loadAttachments();

                if (this.bsModal) this.bsModal.show();
            },

            async loadAttachments() {
                if (this.editTx.id === 'NEW') return;
                try {
                    const res = await api.get(`/attachments/Transaccion/${this.editTx.id}`);
                    this.attachments = res.data || [];
                } catch (e) {
                    // El endpoint de adjuntos puede no existir aún — ignorar silenciosamente
                    if (e.response?.status !== 404) {
                        console.warn('Error cargando adjuntos:', e.message);
                    }
                    this.attachments = [];
                }
            },

            async subirAdjunto(e) {
                const file = e.target.files[0];
                if (!file) return;

                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    this.saving = true;
                    await api.post(`/attachments/?tipo_referencia=Transaccion&id_referencia=${this.editTx.id}`, formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });
                    await this.loadAttachments();
                } catch (e) {
                    alert('Error al subir archivo: ' + (e.response?.data?.detail || 'Fallo desconocido'));
                } finally {
                    this.saving = false;
                    e.target.value = '';
                }
            },

            async procesarOCR(e) {
                const file = e.target.files[0];
                if (!file) return;
                
                const formData = new FormData();
                formData.append('file', file);
                
                try {
                    this.isScanningReceipt = true;
                    // Trigger OCR endpoint
                    const response = await api.post('/ia/ocr', formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                    });
                    
                    const data = response.data;
                    if (data && data.transaction_prefill) {
                        const prefill = data.transaction_prefill;
                        // Auto-fill values
                        if (prefill.amount) {
                            this.editTx.amount = prefill.amount;
                            this.editTx.transaction_code = 'Withdrawal'; // Assume expense by default for tickets
                        }
                        if (prefill.date) {
                            // Extract just the day, to keep hours neutral or respect ISO format up to minutes
                            this.editTx.date = prefill.date.slice(0, 16);
                        }
                        if (prefill.description) {
                            this.editTx.notes = prefill.description + (data.engine ? ` [OCR: ${data.engine}]` : '');
                        }
                        if (prefill.payee_name || prefill.merchant) {
                            // Intentar setear payee name
                            const merchant = prefill.payee_name || prefill.merchant;
                            this.editTx.notes += `\n[Merchant Detectado: ${merchant}]`;
                        }
                        
                        // Handle splits if any
                        if (prefill.splits_suggested && prefill.splits_suggested.length > 0) {
                            this.editTx.is_split = true;
                            this.editTx.splits = prefill.splits_suggested.map(s => ({
                                category_id: null,
                                amount: s.amount,
                                notes: s.description
                            }));
                        }
                        if (typeof NotificationManager !== 'undefined') {
                            NotificationManager.success("Ticket analizado con éxito", "IA OCR");
                        }
                    }
                } catch (e) {
                    if (typeof NotificationManager !== 'undefined') {
                        NotificationManager.error('No se pudieron extraer datos o el archivo es ilegible: ' + (e.response?.data?.detail || e.message || ''), "Error OCR");
                    } else {
                        alert('No se pudieron extraer datos del comprobante proporcionado');
                    }
                } finally {
                    this.isScanningReceipt = false;
                    e.target.value = '';
                }
            },

            async eliminarAdjunto(adjId) {
                if (!await NotificationManager.confirm($store.lang.t('transactions.confirm_delete_attachment'))) return;
                try {
                    await api.delete(`/attachments/${adjId}`);
                    this.attachments = this.attachments.filter(a => a.id_adjunto !== adjId);
                } catch (e) {
                    NotificationManager.error($store.lang.t('transactions.error_delete_attachment'));
                }
            },

            descargarAdjunto(adj) {
                window.open(`${api.defaults.baseURL}/attachments/download/${adj.id_adjunto}`, '_blank');
            },

            toggleTag(tagId) {
                if (!this.editTx.tags) this.editTx.tags = [];
                const idx = this.editTx.tags.indexOf(tagId);
                if (idx > -1) {
                    this.editTx.tags.splice(idx, 1);
                } else {
                    this.editTx.tags.push(tagId);
                }
            },
            
            async guardarCambios() {
                this.saving = true;
                try {
                    let baseAmount = parseFloat(this.editTx.amount || 0);
                    // Generate payload compatible with TransactionCreate
                    let txPayload = {
                        date: this.editTx.date ? new Date(this.editTx.date).toISOString() : new Date().toISOString(),
                        description: this.editTx.notes || null,
                        payee_id: this.editTx.payee_id || null,
                        notes: this.editTx.notes || null,
                        status: this.editTx.status || 'PENDING',
                        tag_ids: this.editTx.tags || [],
                        splits: []
                    };

                    if (this.editTx.transaction_code === 'Transfer') {
                        if (!this.editTx.target_account_id) throw new Error($store.lang.t('transactions.select_destination'));
                        txPayload.description = txPayload.description || `Transferencia de cuenta #${this.editTx.account_id} a #${this.editTx.target_account_id}`;
                        txPayload.splits.push({
                            account_id: this.editTx.account_id,
                            amount: -baseAmount,
                            currency_code: 'ARS'
                        });
                        txPayload.splits.push({
                            account_id: this.editTx.target_account_id,
                            amount: baseAmount,
                            currency_code: 'ARS'
                        });
                    } else {
                        // Withdrawal or Deposit
                        if (this.editTx.transaction_code === 'Withdrawal') {
                            baseAmount = -Math.abs(baseAmount);
                        } else {
                            baseAmount = Math.abs(baseAmount);
                        }

                        if (this.editTx.is_split && this.editTx.splits && this.editTx.splits.length > 0) {
                            this.editTx.splits.forEach(d => {
                                let pAmt = parseFloat(d.amount || 0);
                                if (this.editTx.transaction_code === 'Withdrawal') pAmt = -Math.abs(pAmt);
                                else pAmt = Math.abs(pAmt);
                                
                                txPayload.splits.push({
                                    account_id: this.editTx.account_id,
                                    category_id: d.category_id || null,
                                    amount: pAmt,
                                    currency_code: 'ARS',
                                    memo: d.notas || null
                                });
                            });
                        } else {
                            txPayload.splits.push({
                                account_id: this.editTx.account_id,
                                category_id: this.editTx.category_id || null,
                                amount: baseAmount,
                                currency_code: 'ARS'
                            });
                        }
                    }

                    let response;
                    
                    if (this.editTx.id === 'NEW') {
                        response = await api.post('/transactions/', txPayload);
                        this.applyFilters(); 
                    } else {
                        response = await api.put(`/transactions/${this.editTx.id}`, txPayload);
                        this.applyFilters(); 
                    }
                    if (this.bsModal) this.bsModal.hide();
                } catch (error) {
                    const msg = error.response?.data?.detail || error.message;
                    if (typeof NotificationManager !== 'undefined') {
                        NotificationManager.error((typeof msg === 'object' ? JSON.stringify(msg) : (msg || 'Fallas en enlace neuronal')), $store.lang.t('transactions.error_save'));
                    }
                } finally {
                    this.saving = false;
                }
            },

            confirmDelete() {
                if (!this.selectedTxId) return;
                const msg = this.$store.lang.t('common.delete_confirm') || '¿Está seguro de eliminar esta transacción?';
                if (confirm(msg)) {
                    this.deleteTransaction(this.selectedTxId);
                }
            },

            async deleteTransaction(id) {
                try {
                    await api.delete(`/transactions/${id}`);
                    this.transactions = this.transactions.filter(t => t.id !== id);
                    if (this.selectedTxId === id) this.selectedTxId = null;
                } catch (error) {
                    console.error('Error eliminando:', error);
                    if (typeof NotificationManager !== 'undefined') {
                        NotificationManager.error($store.lang.t('transactions.error_delete_tx'));
                    }
                }
            },

            async duplicateTransaction(id) {
                const tx = this.transactions.find(t => t.id === id);
                if (!tx) return;
                
                // Clone and prepare for new insertion
                this.editTx = JSON.parse(JSON.stringify(tx));
                this.editTx.id = 'NEW';
                this.editTx.date = new Date().toISOString().slice(0, 16);
                
                // Clear linked data that shouldn't be duplicated directly or needs reset
                if (!this.editTx.tags) this.editTx.tags = [];
                if (!this.editTx.splits) this.editTx.splits = [];
                
                this.attachments = []; 
                
                if (this.bsModal) this.bsModal.show();
            },

            toggleSplitMode() {
                if (this.editTx.is_split && this.editTx.splits.length === 0) {
                    this.agregarDivision();
                }
            },

            agregarDivision() {
                if (!this.editTx.splits) this.editTx.splits = [];
                this.editTx.splits.push({
                    category_id: this.collections.categories[0]?.id || null,
                    amount: 0,
                    notes: ''
                });
            },

            quitarDivision(index) {
                this.editTx.splits.splice(index, 1);
            },



            newTransaction() {
                this.editTx = {
                    id: 'NEW',
                    date: new Date().toISOString().slice(0, 16),
                    transaction_code: 'Withdrawal',
                    amount: 0,
                    account_id: this.filters.account_id || '',
                    category_id: '',
                    notes: '',
                    tags: [],
                    is_split: false,
                    splits: []
                };
                this.attachments = [];
                if (this.bsModal) this.bsModal.show();
            },

            // Dual definition of editTransaction removed during consolidation.
            // Using the robust one at line ~444.


            getSplitSum() {
                if (!this.editTx.splits) return 0;
                return this.editTx.splits.reduce((sum, d) => sum + (parseFloat(d.amount) || 0), 0);
            }
        }));
    }

    if (window.Alpine) {
        initTransactionsComponent();
    } else {
        document.addEventListener('alpine:init', initTransactionsComponent);
    }