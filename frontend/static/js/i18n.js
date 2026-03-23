function initI18nStore() {
    if (!window.Alpine) return;
    if (Alpine.store('lang')) return;

    Alpine.store('lang', {
        current: localStorage.getItem('3f_lang') || 'es',
        translations: {},
        loaded: false,

        init() {
            const saved = localStorage.getItem('3f_lang');
            if (saved) {
                this.loadLanguage(saved);
            } else {
                const browserLang = navigator.language.split('-')[0];
                const target = ['es', 'en'].includes(browserLang) ? browserLang : 'es';
                this.loadLanguage(target);
            }
        },

        set(langCode) {
            this.loadLanguage(langCode);
        },

        async loadLanguage(langCode) {
            try {
                console.log('Loading language:', langCode);
                const response = await fetch(`/static/js/lang-${langCode}.json?t=${Date.now()}`);
                if (!response.ok) throw new Error(`Language file for ${langCode} not found.`);
                this.translations = await response.json();
                console.log('Language loaded successfully:', langCode, this.translations);
                this.current = langCode;
                localStorage.setItem('3f_lang', langCode);
                this.loaded = true;
            } catch (error) {
                console.error('Failed to load translations:', error);
                if (langCode !== 'es') this.loadLanguage('es');
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
}

if (window.Alpine) {
    initI18nStore();
} else {
    document.addEventListener('alpine:init', initI18nStore);
}
