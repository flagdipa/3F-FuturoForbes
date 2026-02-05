/**
 * ThemeManager - Handles theme switching with CSS variables
 * Loads user's saved theme and applies it dynamically
 */
class ThemeManager {
    constructor() {
        this.currentTheme = null;
        this.init();
    }

    /**
     * Initialize theme manager
     * Load and apply user's saved theme
     */
    async init() {
        try {
            await this.loadUserTheme();
        } catch (error) {
            console.error('Error loading theme:', error);
            // Fallback to default theme
            this.applyThemeVariables({
                "--3f-bg": "#0a0e27",
                "--3f-primary": "#00f3ff"
                // ... minimal fallback
            });
        }
    }

    /**
     * Load user's saved theme from backend
     */
    async loadUserTheme() {
        try {
            const response = await api.get('/themes/current');
            if (response.data) {
                this.currentTheme = response.data;
                this.applyThemeVariables(response.data.variables);
            }
        } catch (error) {
            console.warn('No saved theme found, using default');
        }
    }

    /**
     * Switch to a different theme
     * @param {string} themeId - Theme ID to switch to
     */
    async switchTheme(themeId) {
        try {
            // Get theme data
            const response = await api.get(`/themes/presets/${themeId}`);
            const theme = response.data;

            // Apply theme variables
            this.applyThemeVariables(theme.variables);

            // Save preference to backend
            await api.put('/themes/current', { theme_id: themeId });

            this.currentTheme = theme;

            // Dispatch event for other components
            window.dispatchEvent(new CustomEvent('theme-changed', {
                detail: { theme }
            }));

            return true;
        } catch (error) {
            console.error('Error switching theme:', error);
            return false;
        }
    }

    /**
     * Apply theme CSS variables to document root
     * @param {Object} variables - CSS variables object
     */
    applyThemeVariables(variables) {
        const root = document.documentElement;

        // Apply each variable
        Object.entries(variables).forEach(([key, value]) => {
            root.style.setProperty(key, value);
        });

        // Add smooth transition
        if (!root.classList.contains('theme-transitioning')) {
            root.classList.add('theme-transitioning');
            setTimeout(() => {
                root.classList.remove('theme-transitioning');
            }, 300);
        }
    }

    /**
     * Get all available themes
     */
    async getAvailableThemes() {
        try {
            const response = await api.get('/themes/presets');
            return response.data;
        } catch (error) {
            console.error('Error loading themes:', error);
            return [];
        }
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.currentTheme;
    }
}

// Global instance
window.themeManager = new ThemeManager();
