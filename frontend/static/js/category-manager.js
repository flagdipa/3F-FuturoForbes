document.addEventListener('alpine:init', () => {
    // Shared store for category form data across different modal instances
    Alpine.store('catForm', {
        id_categoria: null,
        nombre_categoria: '',
        id_padre: null,
        notas: '',
        isEdit: false,
        parentName: 'Raíz (Ninguna)'
    });

    // Shared store for merging logic
    Alpine.store('mergeData', {
        id_origen: '',
        id_destino: '',
        eliminar_origen: false,
        stats: {
            transacciones: 0,
            divisiones: 0,
            programadas: 0,
            divisiones_programadas: 0,
            beneficiarios: 0,
            presupuestos: 0
        }
    });

    Alpine.data('categoryTreeManager', () => ({
        categories: [],
        treeData: [],
        selectedId: null,
        selectedNode: null,
        loading: false,
        searchQuery: '',

        async init() {
            this.$watch('searchQuery', () => this.buildTree());

            // Global listeners
            window.addEventListener('save-category', () => this.saveCat());
            window.addEventListener('fetch-merge-stats', () => this.fetchMergeStats());
            window.addEventListener('execute-merge', () => this.executeMerge());

            window.addEventListener('open-category-manager', async () => {
                const modalEl = document.getElementById('categoryManagerModal');
                const modal = new bootstrap.Modal(modalEl);
                await this.loadData();
                modal.show();
                this.$nextTick(() => {
                    this.initSortable();
                    this.makeDraggable(modalEl);
                });
            });
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
                    content.style.transform = 'none'; // Bootstrap centering override
                };
            };
        },

        async loadData() {
            this.loading = true;
            try {
                const res = await api.get('categorias/');
                const raw = res.data.data || [];

                // Pre-calculate full paths for dropdowns
                Alpine.store('catForm').categories = raw.map(c => ({
                    ...c,
                    full_name: this.calculateFullPath(c, raw)
                }));

                this.buildTree();
            } catch (e) {
                console.error('Error loading categories:', e);
            } finally {
                this.loading = false;
            }
        },

        calculateFullPath(cat, all) {
            let path = cat.nombre_categoria;
            let current = cat;
            let safety = 0;
            while ((current.id_padre || current.id_categoria_padre) && safety < 10) {
                const parentId = current.id_padre || current.id_categoria_padre;
                const parent = all.find(x => x.id_categoria === parentId);
                if (parent) {
                    path = parent.nombre_categoria + ':' + path;
                    current = parent;
                    safety++;
                } else break;
            }
            return path;
        },

        buildTree() {
            const query = this.searchQuery.toLowerCase();
            const map = {};
            const roots = [];
            const categories = Alpine.store('catForm').categories;

            categories.forEach(c => {
                map[c.id_categoria] = { ...c, children: [], collapsed: this.searchQuery ? false : (c.collapsed || false) };
            });

            categories.forEach(c => {
                const parentId = c.id_padre || c.id_categoria_padre;
                if (parentId && map[parentId]) {
                    map[parentId].children.push(map[c.id_categoria]);
                } else {
                    roots.push(map[c.id_categoria]);
                }
            });

            this.treeData = roots.sort((a, b) => a.nombre_categoria.localeCompare(b.nombre_categoria));
        },

        selectCat(cat) {
            this.selectedId = cat.id_categoria;
            this.selectedNode = cat;
        },

        toggleCollapse(cat) {
            cat.collapsed = !cat.collapsed;
        },

        collapseAll() {
            const traverse = (nodes) => {
                nodes.forEach(n => {
                    n.collapsed = true;
                    if (n.children) traverse(n.children);
                });
            };
            traverse(this.treeData);
        },

        expandAll() {
            const traverse = (nodes) => {
                nodes.forEach(n => {
                    n.collapsed = false;
                    if (n.children) traverse(n.children);
                });
            };
            traverse(this.treeData);
        },

        initSortable() {
            const el = document.getElementById('sortable-categories');
            if (!el) return;
            this.setupSortableElement(el);
            document.querySelectorAll('.nested-tree').forEach(nested => {
                this.setupSortableElement(nested);
            });
        },

        setupSortableElement(el) {
            Sortable.create(el, {
                group: 'nested-categories',
                animation: 150,
                fallbackOnBody: true,
                swapThreshold: 0.65,
                handle: '.category-node',
                onEnd: async (evt) => {
                    const id = evt.item.getAttribute('data-id');
                    const newParentEl = evt.to.closest('.category-item');
                    const newParentId = newParentEl ? newParentEl.getAttribute('data-id') : null;

                    if (id === newParentId) return;

                    try {
                        const payload = { id_padre: newParentId ? parseInt(newParentId) : null };
                        await api.put(`categorias/${id}`, payload);
                        await this.loadData();
                        this.$nextTick(() => this.initSortable());
                    } catch (e) {
                        console.error('Move error:', e.response?.data);
                        alert('Error al mover categoría: ' + (e.response?.data?.detail || 'Desconocido'));
                        await this.loadData();
                    }
                }
            });
        },

        updateParentNameInStore(parentId) {
            if (!parentId) {
                Alpine.store('catForm').parentName = 'Raíz (Ninguna)';
                return;
            }
            const parent = Alpine.store('catForm').categories.find(c => c.id_categoria === parentId);
            Alpine.store('catForm').parentName = parent ? parent.nombre_categoria : 'Raíz (Ninguna)';
        },

        createCat() {
            const store = Alpine.store('catForm');
            store.isEdit = false;
            store.id_categoria = null;
            store.nombre_categoria = '';
            store.id_padre = this.selectedId;
            store.notas = '';
            this.updateParentNameInStore(this.selectedId);

            const modalEl = document.getElementById('categoryFormModal');
            let modal = bootstrap.Modal.getOrCreateInstance(modalEl);
            modal.show();
        },

        editCat() {
            if (!this.selectedId) return;
            const store = Alpine.store('catForm');
            store.isEdit = true;
            store.id_categoria = this.selectedNode.id_categoria;
            store.nombre_categoria = this.selectedNode.nombre_categoria;
            store.id_padre = this.selectedNode.id_padre || this.selectedNode.id_categoria_padre;
            store.notas = this.selectedNode.notas || '';
            this.updateParentNameInStore(store.id_padre);

            const modalEl = document.getElementById('categoryFormModal');
            if (modalEl) {
                const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
                modal.show();
            }
        },

        async saveCat() {
            const store = Alpine.store('catForm');
            if (!store.nombre_categoria) return alert('El nombre es obligatorio');

            try {
                if (store.isEdit) {
                    await api.put(`categorias/${store.id_categoria}`, {
                        nombre_categoria: store.nombre_categoria,
                        id_padre: store.id_padre || null,
                        notas: store.notas
                    });
                } else {
                    await api.post('categorias/', {
                        nombre_categoria: store.nombre_categoria,
                        id_padre: store.id_padre,
                        notas: store.notas
                    });
                }

                const modalEl = document.getElementById('categoryFormModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();

                await this.loadData();
                this.$nextTick(() => this.initSortable());
            } catch (e) {
                alert('Error al guardar la categoría');
            }
        },

        async deleteCat() {
            if (!this.selectedId) return;
            if (!confirm(`¿Borrar categoría "${this.selectedNode.nombre_categoria}"?`)) return;

            try {
                await api.delete(`categorias/${this.selectedId}`);
                this.selectedId = null;
                await this.loadData();
                this.$nextTick(() => this.initSortable());
            } catch (e) {
                alert('Error al borrar. Asegúrese que no tiene subcategorías ni transacciones.');
            }
        },

        // --- MERGE LOGIC ---
        openMergeModal() {
            const store = Alpine.store('mergeData');
            store.id_origen = this.selectedId || '';
            store.id_destino = '';
            store.eliminar_origen = false;
            store.stats = { transacciones: 0, divisiones: 0, programadas: 0, divisiones_programadas: 0, beneficiarios: 0, presupuestos: 0 };

            if (store.id_origen) this.fetchMergeStats();

            const modal = new bootstrap.Modal(document.getElementById('categoryMergeModal'));
            modal.show();
        },

        async fetchMergeStats() {
            const store = Alpine.store('mergeData');
            if (!store.id_origen) return;
            try {
                const res = await api.get(`categorias/${store.id_origen}/stats`);
                store.stats = res.data;
            } catch (e) {
                console.error('Error fetching stats:', e);
            }
        },

        async executeMerge() {
            const store = Alpine.store('mergeData');
            if (!store.id_origen || !store.id_destino) return;
            if (store.id_origen == store.id_destino) return alert('La categoría de origen y destino deben ser diferentes');

            if (!confirm('¿Está seguro de que desea combinar estas categorías? Esta acción moverá todas las transacciones y no se puede deshacer.')) return;

            try {
                await api.post('categorias/combinar', {
                    id_origen: parseInt(store.id_origen),
                    id_destino: parseInt(store.id_destino),
                    eliminar_origen: store.eliminar_origen
                });

                const modalEl = document.getElementById('categoryMergeModal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                if (modal) modal.hide();

                await this.loadData();
                this.$nextTick(() => this.initSortable());
                alert('Categorías combinadas correctamente');
            } catch (e) {
                alert('Error al combinar categorías');
            }
        }
    }));
});
