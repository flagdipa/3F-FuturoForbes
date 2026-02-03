/**
 * 3F System - i18n Engine
 * Alpine.js Global Store for Multi-language Support
 */

document.addEventListener('alpine:init', () => {
    Alpine.store('lang', {
        current: localStorage.getItem('3f_lang') || 'es',
        translations: {},
        loaded: false,

        async init() {
            await this.loadLanguage(this.current);
        },

        async loadLanguage(langCode) {
            try {
                const response = await fetch(`/static/js/lang-${langCode}.json`);
                if (!response.ok) throw new Error(`Language file for ${langCode} not found.`);
                this.translations = await response.data || await response.json();
                this.current = langCode;
                localStorage.setItem('3f_lang', langCode);
                this.loaded = true;
                console.log(`Language [${langCode}] loaded successfully.`);
            } catch (error) {
                console.error('Failed to load translations:', error);
                // Fallback to ES if anything fails
                if (langCode !== 'es') await this.loadLanguage('es');
            }
        },

        // Helper to get nested properties safely: $store.lang.t('nav.dashboard')
        t(path) {
            if (!this.loaded) return path;
            const keys = path.split('.');
            let value = this.translations;
            for (const key of keys) {
                if (value && value[key]) {
                    value = value[key];
                } else {
                    return path; // Fallback to path if not found
                }
            }
            return value;
        }
    });
});
