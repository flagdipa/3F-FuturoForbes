/**
 * 3F Transaction Form Controller
 * Premium UX with Math expression evaluation & OCR simulation
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('transactionForm', () => ({
        editMode: false,
        submitting: false,
        scanning: false,
        currencySymbol: '$',
        previewValue: '',

        formData: {
            type: 'EXPENSE',
            amount: '',
            date: new Date().toISOString().split('T')[0],
            account_id: '',
            category_id: '',
            payee_name: '',
            notes: '',
            tags: [],
            reconciled: false
        },

        accounts: [],
        categories: [],
        payees: [],

        async init() {
            // Load base data
            await Promise.all([
                this.loadAccounts(),
                this.loadCategories(),
                this.loadPayees()
            ]);

            // Set default account if available
            if (this.accounts.length > 0) {
                this.formData.account_id = this.accounts[0].id;
            }

            // Global listener to open the modal
            window.addEventListener('open-transaction-form', (e) => {
                this.resetForm();
                if (e.detail && e.detail.tx) {
                    this.loadTransaction(e.detail.tx);
                }
                const modal = new bootstrap.Modal(document.getElementById('transaction-modal'));
                modal.show();
            });
        },

        async loadAccounts() {
            try {
                const res = await api.get('/cuentas/');
                const raw = Array.isArray(res.data) ? res.data : (res.data?.data || []);
                this.accounts = raw.map(a => ({ id: a.id_cuenta, name: a.nombre_cuenta }));
            } catch (e) {
                console.warn('Error loading accounts for form:', e);
                this.accounts = [];
            }
        },

        async loadCategories() {
            try {
                const res = await api.get('/categorias/');
                const raw = Array.isArray(res.data) ? res.data : (res.data?.data || []);
                this.categories = raw.map(c => ({ id: c.id_categoria, name: c.nombre_categoria }));
            } catch (e) {
                console.warn('Error loading categories for form:', e);
                this.categories = [];
            }
        },

        async loadPayees() {
            try {
                const res = await api.get('/beneficiarios/');
                const raw = Array.isArray(res.data) ? res.data : (res.data?.data || []);
                this.payees = raw.map(p => ({ id: p.id_beneficiario, name: p.nombre_beneficiario }));
            } catch (e) {
                console.warn('Error loading payees for form:', e);
                this.payees = [];
            }
        },

        resetForm() {
            this.editMode = false;
            this.formData = {
                type: 'EXPENSE',
                amount: '',
                date: new Date().toISOString().split('T')[0],
                account_id: this.accounts[0]?.id || '',
                category_id: '',
                payee_name: '',
                notes: '',
                tags: [],
                reconciled: false
            };
            this.previewValue = '';
        },

        setDate(val) {
            let d = new Date();
            if (val === 'yesterday') d.setDate(d.getDate() - 1);
            this.formData.date = d.toISOString().split('T')[0];
        },

        addTag(tag) {
            if (tag && !this.formData.tags.includes(tag)) {
                this.formData.tags.push(tag);
            }
        },

        removeTag(tag) {
            this.formData.tags = this.formData.tags.filter(t => t !== tag);
        },

        evaluateExpression() {
            // Simple math evaluation for amount input
            const input = this.formData.amount;
            if (!input || !/[+\-*/]/.test(input)) {
                this.previewValue = '';
                return;
            }

            try {
                // Warning: eval is used here on a limited regex-validated string
                // In production, use a math parser library
                const sanitized = input.replace(/[^0-9+*/.-]/g, '');
                const result = eval(sanitized);
                this.previewValue = Number(result).toFixed(2);
            } catch (e) {
                this.previewValue = 'Error';
            }
        },

        async triggerOCR() {
            this.scanning = true;
            // Simulate AI analysis
            setTimeout(() => {
                this.formData.amount = '4500.50';
                this.formData.payee_name = 'STARBUCKS COFFEE';
                this.formData.category_id = 1; // Comida
                this.formData.tags.push('OCR-AI');
                this.previewValue = '';
                this.scanning = false;
                alert("Análisis de Ticket completado por Gemini Engine.");
            }, 3000);
        },

        handleFileUpload(e) {
            const file = e.target.files[0];
            if (file) {
                this.formData.notes += `\n[Archivo adjunto: ${file.name}]`;
            }
        },

        async submitForm() {
            this.submitting = true;
            try {
                // Final evaluation of expression if any
                if (this.previewValue && this.previewValue !== 'Error') {
                    this.formData.amount = this.previewValue;
                }

                console.log("Submitting Transaction...", this.formData);

                // Simulate API call
                await new Promise(r => setTimeout(r, 1000));

                // Close modal
                const modalEl = document.getElementById('transaction-modal');
                const modal = bootstrap.Modal.getInstance(modalEl);
                modal.hide();

                // Dispatch event to refresh dashboard
                window.dispatchEvent(new CustomEvent('update-data'));

            } catch (e) {
                alert("Error al procesar: " + e.message);
            } finally {
                this.submitting = false;
            }
        }
    }));
});
