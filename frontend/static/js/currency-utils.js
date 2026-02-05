/**
 * 3F System - Currency & Format Utilities
 * Centralized logic for currency conversion and representation
 */

const CurrencyUtils = {
    /**
     * Standard symbols for primary currencies
     */
    SYMBOLS: {
        'ARS': '$',
        'USD': 'u$s',
        'EUR': '€',
        'BTC': '₿',
        'ETH': 'Ξ',
        'GBP': '£'
    },

    /**
     * Formats a numeric value into a currency string
     * @param {number|string} amount - The value to format
     * @param {string} currencyCode - ISO code (e.g., 'ARS', 'USD')
     * @returns {string} Fully formatted currency string
     */
    formatCurrency(amount, currencyCode = 'ARS') {
        const value = parseFloat(amount);
        if (isNaN(value)) return '$ 0,00';

        const prefix = this.SYMBOLS[currencyCode] || '$';

        // Crypto formatting (high precision)
        if (currencyCode === 'BTC' || currencyCode === 'ETH') {
            return `${prefix} ${value.toFixed(8)}`;
        }

        // Standard Fiat formatting (2 decimals, local separator)
        return `${prefix} ${value.toLocaleString('es-AR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        })}`;
    },

    /**
     * Converts an amount from one currency to another given a baseline rate
     * @param {number} amount - Amount in source currency
     * @param {number} rate - Conversion rate (base / source)
     * @returns {number} Converted value
     */
    convert(amount, rate) {
        return amount * (rate || 1);
    }
};

// Export for window or module
if (typeof window !== 'undefined') {
    window.CurrencyUtils = CurrencyUtils;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CurrencyUtils;
}
