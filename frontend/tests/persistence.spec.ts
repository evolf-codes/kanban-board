import { expect, test } from "@playwright/test";
import { signIn } from "./helpers";

test("persists a renamed column after reload", async ({ page }) => {
  await signIn(page);

  const columnTitle = page
    .getByTestId("column-col-backlog")
    .getByLabel("Column title");
  const uniqueTitle = `Persisted ${Date.now()}`;
  await columnTitle.fill(uniqueTitle);
  await columnTitle.blur();

  await expect(page.getByText(uniqueTitle).first()).toBeVisible();
  await expect(page.getByText("Saving...")).toBeHidden();

  await page.reload();
  await expect(page.getByText("Loading board...")).toBeHidden();
  await expect(
    page.getByTestId("column-col-backlog").getByLabel("Column title")
  ).toHaveValue(uniqueTitle);
});

test("persists a new card after reload", async ({ page }) => {
  await signIn(page);

  const uniqueTitle = `Persisted card ${Date.now()}`;
  const column = page.getByTestId("column-col-review");
  await column.getByRole("button", { name: /add a card/i }).click();
  await column.getByPlaceholder("Card title").fill(uniqueTitle);
  await column.getByPlaceholder("Details").fill("Saved in SQLite.");
  await column.getByRole("button", { name: /add card/i }).click();

  await expect(column.getByText(uniqueTitle)).toBeVisible();
  await expect(page.getByText("Saving...")).toBeHidden();

  await page.reload();
  await expect(page.getByText("Loading board...")).toBeHidden();
  await expect(page.getByText(uniqueTitle)).toBeVisible();
});
