import { sendChat } from "@/lib/ai-api";

describe("sendChat", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns the chat response on success", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => "application/json" },
        json: async () => ({
          message: "Done.",
          boardUpdated: false,
          board: null,
        }),
      })
    );

    const response = await sendChat("Hi", []);

    expect(response.message).toBe("Done.");
  });

  it("surfaces API error details", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        headers: { get: () => "application/json" },
        json: async () => ({ detail: "Unknown card_id: card-missing." }),
      })
    );

    await expect(sendChat("Delete it", [])).rejects.toThrow(
      "Unknown card_id: card-missing."
    );
  });
});
