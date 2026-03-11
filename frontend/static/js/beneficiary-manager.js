document.addEventListener('alpine:init', () => {
    // Shared store for beneficiary form data
    Alpine.store('benefForm', {
        id_beneficiario: null,
        nombre_beneficiario: '',
        sitio_web: '',
        notas: '',
        cbu: '',
        cuit: '',
        telefono: '',
        direccion: '',
        banco: '',
        activo: 1,
        isEdit: false
    });

    // Shared store for manager state (beneficiaries list and transaction details)
    Alpine.store('benefManager', {
        beneficiaries: [],
        loading: false,
        beneficiaryTx: [],
        loadingTx: false,
        selectedNode: null,
        selectedId: null,
        showHidden: false,
        searchQuery: '',

        async loadData() {
            this.loading = true;
            try {
                const res = await api.get('beneficiarios/');
                this.beneficiaries = Array.isArray(res.data) ? res.data : (res.data?.data || []);
            } catch (e) {
                console.error('Error loading beneficiaries:', e);
            } finally {
                this.loading = false;
            }
        },

        async viewTransactions(item) {
            if (!item) return;
            console.log('Viewing transactions for beneficiary:', item.id_beneficiario, item.nombre_beneficiario);
            this.selectedNode = { ...item }; // Copy object for stability
            this.selectedId = item.id_beneficiario;
            this.beneficiaryTx = [];
            this.loadingTx = true;

            // Show modal first, then fetch
            const txModalEl = document.getElementById('beneficiaryTransactionsModal');
            if (txModalEl) {
                const modal = bootstrap.Modal.getOrCreateInstance(txModalEl);
                modal.show();
            }

            try {
                const res = await api.get('transactions/', {
                    params: {
                        id_beneficiario: item.id_beneficiario,
                        limit: 50
                    }
                });

                let txList = Array.isArray(res.data) ? res.data : (res.data?.data || []);

                // Map to what the template expects
                txList = txList.map(tx => {
                    let amount = 0;
                    let type = "Unknown";
                    if (tx.splits && tx.splits.length > 0) {
                        amount = Math.abs(parseFloat(tx.splits[0].amount));
                        type = parseFloat(tx.splits[0].amount) > 0 ? "Ingreso" : "Gasto";
                    }
                    return {
                        id_transaccion: tx.id,
                        fecha_transaccion: tx.date,
                        monto_transaccion: amount,
                        descripcion: tx.description || tx.notes || '',
                        estado: (tx.status === 'RECONCILED' || tx.status === 1) ? 'Conciled' : 'None',
                        tipo_transaccion: type
                    };
                });

                console.log(`Transactions loaded for beneficiary ${item.id_beneficiario}:`, txList.length, 'items');
                if (txList.length === 0) {
                    console.warn('Returned 0 transactions. Check that id_beneficiario is stored correctly in libro_transacciones.');
                }
                this.beneficiaryTx = txList;
            } catch (e) {
                console.error('Error loading transactions for beneficiary:', item.id_beneficiario, e);
                this.beneficiaryTx = [];
                if (typeof NotificationManager !== 'undefined') {
                    NotificationManager.error('Error al cargar movimientos del beneficiario');
                }
            } finally {
                this.loadingTx = false;
            }
        }
    });

    Alpine.data('beneficiaryManager', () => ({
        async init() {
            window.addEventListener('save-beneficiary', () => this.saveItem());

            window.addEventListener('open-beneficiary-manager', async () => {
                const modalEl = document.getElementById('beneficiaryManagerModal');
                const modal = bootstrap.Modal.getOrCreateInstance(modalEl);

                await this.$store.benefManager.loadData();
                modal.show();

                this.$nextTick(() => {
                    this.makeDraggable(modalEl);
                    const txModalEl = document.getElementById('beneficiaryTransactionsModal');
                    if (txModalEl) this.makeDraggable(txModalEl);
                });
            });
        },

        get filtered() {
            const store = this.$store.benefManager;
            let list = store.beneficiaries;
            if (!store.showHidden) {
                list = list.filter(b => (b.activo === 1 && b.oculto === 0));
            }
            if (store.searchQuery) {
                const q = store.searchQuery.toLowerCase();
                list = list.filter(b =>
                    b.nombre_beneficiario.toLowerCase().includes(q) ||
                    (b.cuit && b.cuit.includes(q)) ||
                    (b.cbu && b.cbu.includes(q))
                );
            }
            return list.sort((a, b) => a.nombre_beneficiario.localeCompare(b.nombre_beneficiario));
        },

        makeDraggable(el) {
            const header = el.querySelector('.modal-header');
            const content = el.querySelector('.modal-content');
            if (!header || !content) return;

            let pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
            header.style.cursor = 'move';

            header.onmousedown = (e) => {
                if (e.target.closest('.btn-close')) return;
                e = e || window.event;
                e.preventDefault();
                pos3 = e.clientX;
                pos4 = e.clientY;
                document.onmouseup = () => {
                    document.onmouseup = null;
                    document.onmousemove = null;
                };
                document.onmousemove = (e) => {
                    e = e || window.event;
                    e.preventDefault();
                    pos1 = pos3 - e.clientX;
                    pos2 = pos4 - e.clientY;
                    pos3 = e.clientX;
                    pos4 = e.clientY;
                    content.style.position = 'absolute';
                    content.style.top = (content.offsetTop - pos2) + "px";
                    content.style.left = (content.offsetLeft - pos1) + "px";
                    content.style.margin = '0';
                    content.style.transform = 'none';
                };
            };
        },

        createItem() {
            const store = Alpine.store('benefForm');
            store.isEdit = false;
            store.id_beneficiario = null;
            store.nombre_beneficiario = '';
            store.sitio_web = '';
            store.notas = '';
            store.cbu = '';
            store.cuit = '';
            store.telefono = '';
            store.direccion = '';
            store.banco = '';
            store.activo = 1;

            const modalEl = document.getElementById('beneficiaryFormModal');
            let modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();
        },

        editItem() {
            const mStore = this.$store.benefManager;
            if (!mStore.selectedId) return;
            const store = Alpine.store('benefForm');
            store.isEdit = true;
            store.id_beneficiario = mStore.selectedNode.id_beneficiario;
            store.nombre_beneficiario = mStore.selectedNode.nombre_beneficiario;
            store.sitio_web = mStore.selectedNode.sitio_web || '';
            store.notas = mStore.selectedNode.notas || '';
            store.cbu = mStore.selectedNode.cbu || '';
            store.cuit = mStore.selectedNode.cuit || '';
            store.telefono = mStore.selectedNode.telefono || '';
            store.direccion = mStore.selectedNode.direccion || '';
            store.banco = mStore.selectedNode.banco || '';
            store.activo = mStore.selectedNode.activo;

            const modalEl = document.getElementById('beneficiaryFormModal');
            if (modalEl) {
                const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                modal.show();
            }
        },

        async saveItem() {
            const store = Alpine.store('benefForm');
            if (!store.nombre_beneficiario) return alert('El nombre es obligatorio');
            try {
                const payload = {
                    nombre_beneficiario: store.nombre_beneficiario,
                    sitio_web: store.sitio_web,
                    notas: store.notas,
                    cbu: store.cbu,
                    cuit: store.cuit,
                    telefono: store.telefono,
                    direccion: store.direccion,
                    banco: store.banco,
                    activo: store.activo
                };

                if (store.isEdit) {
                    await api.put(`beneficiarios/${store.id_beneficiario}`, payload);
                } else {
                    await api.post('beneficiarios/', payload);
                }
                const modal = bootstrap.Modal.getInstance(document.getElementById('beneficiaryFormModal'));
                if (modal) modal.hide();
                await this.$store.benefManager.loadData();
            } catch (e) { alert('Error al guardar'); }
        },

        async deleteItem() {
            const mStore = this.$store.benefManager;
            if (!mStore.selectedId) return;
            if (!confirm(`¿Borrar beneficiario "${mStore.selectedNode.nombre_beneficiario}"?`)) return;
            try {
                await api.delete(`beneficiarios/${mStore.selectedId}`);
                mStore.selectedId = null;
                await mStore.loadData();
            } catch (e) { alert('Error al borrar. Asegúrese que no tiene transacciones asociadas.'); }
        }
    }));
});
