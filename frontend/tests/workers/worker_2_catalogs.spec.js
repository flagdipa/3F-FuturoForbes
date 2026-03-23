const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

let errorsList = [];

test.beforeEach(async ({ page }) => {
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errorsList.push(`[Console JS Error] ${page.url()}: ${msg.text()}`);
    }
  });

  page.on('response', resp => {
    if (resp.status() >= 400 && resp.url().includes('/api/')) {
        errorsList.push(`[API Error ${resp.status()}] ${resp.url()} -> ${resp.statusText()}`);
    }
  });
});

test('Auditoría E2E: Worker 2 - Categorías y Beneficiarios', async ({ page }) => {
    try {
        await page.goto('/login');
        if (await page.locator('input[type="email"]').count() > 0) {
            await page.fill('input[type="email"]', 'qa_test@example.com');
            await page.fill('input[type="password"]', 'Password123!');
            await page.click('button[type="submit"]');
            await page.waitForTimeout(2000);
        }
        
        // Pruebas sobre la jerarquía de Categorías
        await page.goto('/categories');
        await page.waitForTimeout(2000);
        // Interactuar con algo, esto forzará eventos UI de Alpine JS
        const newCatBtn = page.getByRole('button', { name: /nuevo/i }).first();
        if (await newCatBtn.isVisible()) {
            await newCatBtn.click();
            await page.waitForTimeout(500);
            await page.keyboard.press('Escape');
        }
        
        // Pruebas sobre la gestión de Payees/Beneficiarios
        await page.goto('/beneficiaries');
        await page.waitForTimeout(2000);
        const newBenBtn = page.getByRole('button', { name: /nuevo/i }).first();
        if (await newBenBtn.isVisible()) {
            await newBenBtn.click();
            await page.waitForTimeout(500);
            await page.keyboard.press('Escape');
        }
    } catch (e) {
        errorsList.push(`[Worker 2 Fatal Playwright Exception]: ${e.message}`);
    }
});

test.afterAll(() => {
    const reportPath = path.resolve(__dirname, '../../../../openspec/changes/multi-agent-e2e-orchestration/worker_2_report.md');
    // Ensure dir exists or just write directly since the parent path exists
    let content = `# Reporte Worker 2 (Catálogos y Beneficiarios)\n\n`;
    content += `**Fallos Extraídos en Fase 2:**\n\n`;
    if (errorsList.length === 0) content += `- 0 errores encontrados en las interacciones simuladas.\n`;
    else errorsList.forEach(e => content += `- ${e}\n`);
    
    fs.writeFileSync(reportPath, content);
});
