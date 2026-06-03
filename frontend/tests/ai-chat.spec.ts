import { expect, test } from "@playwright/test";
import { signIn } from "./helpers";

test("sends a chat message and renders the assistant reply", async ({ page }) => {
  await page.route("**/api/ai/chat", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        message: "The backlog has two cards.",
        boardUpdated: false,
        board: null,
      }),
    });
  });

  await signIn(page);

  await page.getByTestId("ai-chat-input").fill("What is in backlog?");
  await page.getByTestId("ai-chat-send").click();

  await expect(page.getByTestId("ai-chat-message-user")).toHaveText(
    "What is in backlog?"
  );
  await expect(page.getByTestId("ai-chat-message-assistant")).toHaveText(
    "The backlog has two cards."
  );
});

test("refreshes the board after an AI update", async ({ page }) => {
  await signIn(page);

  const backlogTitle = page
    .getByTestId("column-col-backlog")
    .getByLabel("Column title");

  await expect(backlogTitle).toHaveValue("Backlog");

  await page.route("**/api/ai/chat", async (route) => {
    const boardResponse = await page.request.get("http://127.0.0.1:8001/api/board", {
      headers: route.request().headers(),
    });
    const board = await boardResponse.json();
    board.columns = board.columns.map(
      (column: { id: string; title: string; cardIds: string[] }) =>
        column.id === "col-backlog" ? { ...column, title: "Ideas" } : column
    );

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        message: "Renamed backlog to Ideas.",
        boardUpdated: true,
        board,
      }),
    });
  });

  await page.getByTestId("ai-chat-input").fill("Rename backlog to Ideas");
  await page.getByTestId("ai-chat-send").click();

  await expect(page.getByTestId("ai-chat-message-assistant")).toHaveText(
    /renamed backlog/i
  );
  await expect(backlogTitle).toHaveValue("Ideas");
});
