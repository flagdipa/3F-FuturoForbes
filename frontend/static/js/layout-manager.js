/**
 * LayoutManager - Handles GridStack layout persistence
 * Automatically saves and loads widget positions per page
 */
class LayoutManager {
    constructor(pageName, grid) {
        this.pageName = pageName;
        this.grid = grid;
        this.saveTimeoutId = null;
        this.DEBOUNCE_DELAY = 1000; // 1 second debounce
        this.saving = false;

        // Attach event listeners
        this.attachListeners();
    }

    /**
     * Attach GridStack event listeners
     */
    attachListeners() {
        if (this.grid) {
            this.grid.on('change', () => {
                this.debouncedSave();
            });
        }

        // Save on page unload (if changes pending)
        window.addEventListener('beforeunload', () => {
            if (this.saveTimeoutId) {
                this.saveLayout(); // Immediate save
            }
        });
    }

    /**
     * Debounced save to avoid excessive API calls
     */
    debouncedSave() {
        if (this.saveTimeoutId) {
            clearTimeout(this.saveTimeoutId);
        }

        this.saveTimeoutId = setTimeout(() => {
            this.saveLayout();
            this.saveTimeoutId = null;
        }, this.DEBOUNCE_DELAY);
    }

    /**
     * Save current layout to backend
     */
    async saveLayout() {
        if (!this.grid || this.saving) return;

        this.saving = true;
        this.showSavingIndicator();

        try {
            const layout = this.grid.save(false); // Get current positions

            await api.post(`/layouts/${this.pageName}`, {
                layout_config: layout
            });

            this.showSavedIndicator();
        } catch (error) {
            console.error('Error saving layout:', error);
            this.showErrorIndicator();
        } finally {
            this.saving = false;
        }
    }

    /**
     * Load saved layout from backend
     */
    async loadLayout() {
        try {
            const response = await api.get(`/layouts/${this.pageName}`);

            if (response.data && response.data.layout_config) {
                this.grid.load(response.data.layout_config);
                console.log(`✅ Loaded custom layout for ${this.pageName}`);
                return true;
            }
        } catch (error) {
            if (error.response

                ?.status === 404) {
                console.log(`ℹ️ No custom layout found for ${this.pageName}, using defaults`);
            } else {
                console.error('Error loading layout:', error);
            }
        }
        return false;
    }

    /**
     * Reset layout to defaults
     */
    async resetLayout() {
        if (!confirm('¿Restablecer el diseño a los valores predeterminados?')) {
            return false;
        }

        try {
            await api.delete(`/layouts/${this.pageName}`);

            // Reload page to apply defaults
            window.location.reload();
            return true;
        } catch (error) {
            console.error('Error resetting layout:', error);
            alert('Error al restablecer el diseño');
            return false;
        }
    }

    /**
     * Visual indicators
     */
    showSavingIndicator() {
        const el = document.getElementById('layout-status');
        if (el) {
            el.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i>Guardando...';
            el.className = 'text-dim small';
        }
    }

    showSavedIndicator() {
        const el = document.getElementById('layout-status');
        if (el) {
            el.innerHTML = '<i class="fa-solid fa-check me-1 text-success"></i>Guardado';
            el.className = 'text-success small';

            // Clear after 2 seconds
            setTimeout(() => {
                el.innerHTML = '';
            }, 2000);
        }
    }

    showErrorIndicator() {
        const el = document.getElementById('layout-status');
        if (el) {
            el.innerHTML = '<i class="fa-solid fa-exclamation-triangle me-1 text-warning"></i>Error';
            el.className = 'text-warning small';
        }
    }
}

// Export for use in Alpine.js components
window.LayoutManager = LayoutManager;
