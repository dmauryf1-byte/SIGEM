import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: 'tests/e2e',
  use: { baseURL: 'http://127.0.0.1:8000', viewport: { width: 1280, height: 800 } },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } },
    },
  ],
  webServer: {
    command: 'uv run --directory ../backend uvicorn app.main:app --port 8000',
    url: 'http://127.0.0.1:8000/',
    reuseExistingServer: true,
  },
});
