const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests/workers',   // Directory where workers will drop their tests
  timeout: 30000,
  expect: {
    timeout: 5000
  },
  fullyParallel: true,          // Can run multiple workers in parallel
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:8000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
