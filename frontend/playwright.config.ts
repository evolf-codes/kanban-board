import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  timeout: 60_000,
  fullyParallel: false,
  workers: 1,
  expect: {
    timeout: 15_000,
  },
  use: {
    baseURL: "http://127.0.0.1:3000",
    trace: "retain-on-failure",
  },
  webServer: [
    {
      command:
        'sh -c "rm -f /tmp/pm-playwright.db && cd ../backend && python3 -m uv sync --no-dev 2>/dev/null; DATABASE_PATH=/tmp/pm-playwright.db PYTHONPATH=. python3 -m uv run --no-dev uvicorn app.main:app --host 127.0.0.1 --port 8001"',
      url: "http://127.0.0.1:8001/api/health",
      reuseExistingServer: false,
      timeout: 120_000,
    },
    {
      command:
        "PLAYWRIGHT_BACKEND=http://127.0.0.1:8001 npm run dev -- --hostname 127.0.0.1 --port 3000",
      url: "http://127.0.0.1:3000",
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
    },
  ],
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
