import { initialData } from "@/lib/kanban";
import { createCard, fetchBoard, renameColumn } from "@/lib/board-api";

describe("board-api", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("fetchBoard loads board data", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => initialData,
      })
    );

    const board = await fetchBoard();

    expect(board.columns).toHaveLength(5);
    expect(board.cards["card-1"].title).toBe("Align roadmap themes");
  });

  it("renameColumn sends a patch request", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => "application/json" },
      json: async () => initialData,
    });
    vi.stubGlobal("fetch", fetchMock);

    await renameColumn("col-backlog", "Ideas");

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/columns/col-backlog",
      expect.objectContaining({
        method: "PATCH",
        body: JSON.stringify({ title: "Ideas" }),
      })
    );
  });

  it("createCard sends card details to the API", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      headers: { get: () => "application/json" },
      json: async () => initialData,
    });
    vi.stubGlobal("fetch", fetchMock);

    await createCard("col-backlog", "New card", "Notes");

    expect(fetchMock).toHaveBeenCalledWith(
      "/api/cards",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          column_id: "col-backlog",
          title: "New card",
          details: "Notes",
        }),
      })
    );
  });
});
