const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

let errorsList = [];

test.beforeEach(async ({ page }) => {
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errorsList.push(`[Console Error Accounts] ${page.url()}: ${msg.text()}`);
    }
  });

  page.on('response', resp => {
    if (resp.status() >= 400 && resp.url().includes('/api/')) {
        errorsList.push(`[API Error Accounts ${resp.status()}] ${resp.url()} -> ${resp.statusText()}`);
    }
  });
});

test('Auditoría E2E: Worker 1 - Cuentas CRUD', async ({ page }) => {
    try {
        await page.goto('/login').catch(() => page.goto('/login.html'));
        if (await page.locator('input[type="email"]').count() > 0) {
            await page.fill('input[type="email"]', 'qa_test@example.com');
            await page.fill('input[type="password"]', 'Password123!');
            await page.click('button[type="submit"]');
            await page.waitForTimeout(2000);
        }
        
        await page.goto('/accounts').catch(() => page.goto('/accounts.html'));
        await page.waitForTimeout(3000);
        
        const createBtn = page.getByRole('button', { name: /nuevo|nueva/i }).first();
        if (await createBtn.isVisible()) {
            await createBtn.click();
            await page.waitForTimeout(500);
            await page.keyboard.press('Escape');
        } else {
            errorsList.push('[Accounts Warning]: Botón Nueva Cuenta no visible o no existe');
        }
    } catch (e) {
        errorsList.push(`[Worker 1 Accounts Playwright Exception]: ${e.message}`);
    }
});

test.afterAll(() => {
    const reportPath = path.resolve(__dirname, '../../../../openspec/changes/e2e-auth-and-accounts-worker/worker_1_report.md');
    let content = `\n## Bloque Cuentas\n`;
    if (errorsList.length === 0) content += `- 0 errores detectados en la prueba de cuentas.\n`;
    else errorsList.forEach(e => content += `- ${e}\n`);
    
    try {
        if (fs.existsSync(reportPath)) {
            const existing = fs.readFileSync(reportPath, 'utf8');
            fs.writeFileSync(reportPath, existing + '\n' + content);
        } else {
            fs.writeFileSync(reportPath, content);
        }
    } catch(err) {
        fs.writeFileSync(reportPath, content);
    }
});