import { render, screen } from "@testing-library/react";
import { AppGate } from "@/components/AppGate";
import { initialData } from "@/lib/kanban";

vi.mock("@/lib/board-api", () => ({
  fetchBoard: vi.fn(),
  renameColumn: vi.fn(),
  createCard: vi.fn(),
  deleteCard: vi.fn(),
  moveCardOnBoard: vi.fn(),
}));

import { fetchBoard } from "@/lib/board-api";

describe("AppGate", () => {
  it("shows the login form when there is no active session", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: { get: () => "application/json" },
        json: async () => ({ authenticated: false, username: null }),
      })
    );

    render(<AppGate />);

    expect(await screen.findByRole("heading", { name: "Sign in" })).toBeInTheDocument();
  });

  it("shows the kanban board for an authenticated session", async () => {
    vi.mocked(fetchBoard).mockResolvedValue(initialData);
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        headers: { get: () => "application/json" },
        json: async () => ({ authenticated: true, username: "user" }),
      })
    );

    render(<AppGate />);

    expect(
      await screen.findByRole("heading", { name: "Kanban Studio" })
    ).toBeInTheDocument();
  });
});
