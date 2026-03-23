const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

let errorsList = [];

test.beforeEach(async ({ page }) => {
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errorsList.push(`[Console Error Auth] ${page.url()}: ${msg.text()}`);
    }
  });

  page.on('response', resp => {
    if (resp.status() >= 400 && resp.url().includes('/api/')) {
        errorsList.push(`[API Error Auth ${resp.status()}] ${resp.url()} -> ${resp.statusText()}`);
    }
  });
});

test('Auditoría E2E: Worker 1 - Autenticación', async ({ page }) => {
    try {
        await page.goto('/login').catch(() => page.goto('/login.html'));
        
        if (await page.locator('input[type="email"]').count() > 0) {
            // Invalid credentials
            await page.fill('input[type="email"]', 'wrong@example.com');
            await page.fill('input[type="password"]', 'badpass');
            await page.click('button[type="submit"]');
            await page.waitForTimeout(1000);
            
            // Valid credentials
            await page.fill('input[type="email"]', 'qa_test@example.com');
            await page.fill('input[type="password"]', 'Password123!');
            await page.click('button[type="submit"]');
            await page.waitForTimeout(2000);
        }
        
        // Register page
        await page.goto('/register').catch(() => page.goto('/register.html'));
        await page.waitForTimeout(1000);
    } catch (e) {
        errorsList.push(`[Worker 1 Auth Playwright Exception]: ${e.message}`);
    }
});

test.afterAll(() => {
    const reportPath = path.resolve(__dirname, '../../../../openspec/changes/e2e-auth-and-accounts-worker/worker_1_report.md');
    // Asegurarse de que el directorio exista
    const dir = path.dirname(reportPath);
    if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
    }
    
    let content = `# Reporte Worker 1 (Auth y Cuentas)\n\n## Bloque Auth\n`;
    if (errorsList.length === 0) content += `- 0 errores detectados en la prueba de autenticación.\n`;
    else errorsList.forEach(e => content += `- ${e}\n`);
    
    fs.writeFileSync(reportPath, content);
});