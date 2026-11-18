import { defineConfig, devices } from '@playwright/test';

// El navegador entra por Flask (5000), que sirve las páginas y reenvía /api a FastAPI (8000)
export default defineConfig({
  testDir: 'tests/e2e',
  globalSetup: './tests/e2e/global-setup.js',
  use: { baseURL: 'http://127.0.0.1:5000', viewport: { width: 1280, height: 800 } },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } },
    },
  ],
  webServer: [
    {
      command: 'uv run --directory ../backend uvicorn app.main:app --port 8000',
      url: 'http://127.0.0.1:8000/api/v1/health',
      reuseExistingServer: true,
    },
    {
      command: 'uv run --directory ../web flask --app app run --port 5000',
      url: 'http://127.0.0.1:5000/',
      reuseExistingServer: true,
    },
  ],
});
