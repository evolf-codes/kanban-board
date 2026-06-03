import { expect, type Page } from "@playwright/test";

export async function signIn(page: Page) {
  await page.goto("/");
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: /^sign in$/i }).click();
  await expect(page.getByText("Loading board...")).toBeHidden({ timeout: 15_000 });
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
}
