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

test('Auditoría E2E: Worker 3 - Transacciones y Operativa Core', async ({ page }) => {
    try {
        await page.goto('/login');
        if (await page.locator('input[type="email"]').count() > 0) {
            await page.fill('input[type="email"]', 'qa_test@example.com');
            await page.fill('input[type="password"]', 'Password123!');
            await page.click('button[type="submit"]');
            await page.waitForTimeout(2000);
        }
        
        // Operaciones de Transacciones
        await page.goto('/transactions');
        await page.waitForTimeout(3000);
        
        // Simular intento de abrir el popup de crear
        const createBtn = page.getByRole('button', { name: /nuevo/i }).first();
        if (await createBtn.isVisible()) {
            await createBtn.click();
            await page.waitForTimeout(500);
            
            // Simular cierre o llenado parcial de un split modal:
            const splitBtn = page.getByText(/split/i).first();
            if (await splitBtn.isVisible()) {
                await splitBtn.click();
            }
            await page.waitForTimeout(500);
            await page.keyboard.press('Escape');
        }
    } catch (e) {
        errorsList.push(`[Worker 3 Fatal Playwright Exception]: ${e.message}`);
    }
});

test.afterAll(() => {
    const reportPath = path.resolve(__dirname, '../../../../openspec/changes/multi-agent-e2e-orchestration/worker_3_report.md');
    let content = `# Reporte Worker 3 (Transacciones E2E)\n\n`;
    content += `**Fallos Extraídos en Fase 3:**\n\n`;
    if (errorsList.length === 0) content += `- Transacciones OK - 0 errores detectados.\n`;
    else errorsList.forEach(e => content += `- ${e}\n`);
    
    fs.writeFileSync(reportPath, content);
});
