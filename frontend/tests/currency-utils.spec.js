const { test, expect } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

test.describe('CurrencyUtils Unit Tests', () => {
    let scriptContent;

    test.beforeAll(async () => {
        const scriptPath = path.resolve(__dirname, '../static/js/currency-utils.js');
        scriptContent = fs.readFileSync(scriptPath, 'utf8');
    });

    test('should format ARS correctly', async ({ page }) => {
        await page.setContent('<html><body></body></html>');
        await page.addScriptTag({ content: scriptContent });

        const result = await page.evaluate(() => CurrencyUtils.formatCurrency(1234.56, 'ARS'));
        expect(result).toMatch(/\$\s*1\.234,56/);
    });

    test('should format USD correctly', async ({ page }) => {
        await page.setContent('<html><body></body></html>');
        await page.addScriptTag({ content: scriptContent });

        const result = await page.evaluate(() => CurrencyUtils.formatCurrency(1234.56, 'USD'));
        expect(result).toMatch(/u\$s\s*1\.234,56/);
    });

    test('should format EUR correctly', async ({ page }) => {
        await page.setContent('<html><body></body></html>');
        await page.addScriptTag({ content: scriptContent });

        const result = await page.evaluate(() => CurrencyUtils.formatCurrency(1234.56, 'EUR'));
        expect(result).toMatch(/€\s*1\.234,56/);
    });

    test('should format BTC with 8 decimals', async ({ page }) => {
        await page.setContent('<html><body></body></html>');
        await page.addScriptTag({ content: scriptContent });

        const result = await page.evaluate(() => CurrencyUtils.formatCurrency(0.12345678, 'BTC'));
        expect(result).toMatch(/₿\s*0\.12345678/);
    });

    test('should format ETH with 8 decimals', async ({ page }) => {
        await page.setContent('<html><body></body></html>');
        await page.addScriptTag({ content: scriptContent });

        const result = await page.evaluate(() => CurrencyUtils.formatCurrency(0.12345678, 'ETH'));
        expect(result).toMatch(/Ξ\s*0\.12345678/);
    });

    test('should handle invalid amounts gracefully', async ({ page }) => {
        await page.setContent('<html><body></body></html>');
        await page.addScriptTag({ content: scriptContent });

        const result = await page.evaluate(() => CurrencyUtils.formatCurrency('invalid', 'ARS'));
        expect(result).toMatch(/\$\s*0,00/);
    });

    test('should convert amounts correctly', async ({ page }) => {
        await page.setContent('<html><body></body></html>');
        await page.addScriptTag({ content: scriptContent });

        const rateUSD_ARS = 800;
        const result = await page.evaluate((r) => CurrencyUtils.convert(100, r), rateUSD_ARS);
        expect(result).toBe(80000);
    });
});
