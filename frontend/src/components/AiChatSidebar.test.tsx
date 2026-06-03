import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AiChatSidebar } from "@/components/AiChatSidebar";
import * as aiApi from "@/lib/ai-api";
import { initialData } from "@/lib/kanban";

vi.mock("@/lib/ai-api", () => ({
  sendChat: vi.fn(),
}));

describe("AiChatSidebar", () => {
  it("renders the sidebar and empty state", () => {
    render(<AiChatSidebar onBoardUpdate={() => undefined} />);

    expect(screen.getByTestId("ai-chat-sidebar")).toBeInTheDocument();
    expect(screen.getByText(/try "what cards are in review/i)).toBeInTheDocument();
  });

  it("shows assistant response after sending a message", async () => {
    vi.mocked(aiApi.sendChat).mockResolvedValue({
      message: "You have three columns with cards.",
      boardUpdated: false,
      board: null,
    });

    render(<AiChatSidebar onBoardUpdate={() => undefined} />);

    await userEvent.type(
      screen.getByTestId("ai-chat-input"),
      "What is on the board?"
    );
    await userEvent.click(screen.getByTestId("ai-chat-send"));

    await waitFor(() => {
      expect(screen.getByTestId("ai-chat-message-user")).toHaveTextContent(
        "What is on the board?"
      );
    });
    expect(screen.getByTestId("ai-chat-message-assistant")).toHaveTextContent(
      "You have three columns with cards."
    );
    expect(aiApi.sendChat).toHaveBeenCalledWith("What is on the board?", []);
  });

  it("refreshes the board when the assistant applies updates", async () => {
    const updatedBoard = {
      ...initialData,
      columns: initialData.columns.map((column) =>
        column.id === "col-backlog" ? { ...column, title: "Ideas" } : column
      ),
    };
    const onBoardUpdate = vi.fn();

    vi.mocked(aiApi.sendChat).mockResolvedValue({
      message: "Renamed the backlog column.",
      boardUpdated: true,
      board: updatedBoard,
    });

    render(<AiChatSidebar onBoardUpdate={onBoardUpdate} />);

    await userEvent.type(screen.getByTestId("ai-chat-input"), "Rename backlog");
    await userEvent.click(screen.getByTestId("ai-chat-send"));

    await waitFor(() => {
      expect(onBoardUpdate).toHaveBeenCalledWith(updatedBoard);
    });
  });

  it("shows an error when chat fails", async () => {
    vi.mocked(aiApi.sendChat).mockRejectedValue(new Error("Chat request failed."));

    render(<AiChatSidebar onBoardUpdate={() => undefined} />);

    await userEvent.type(screen.getByTestId("ai-chat-input"), "Hello");
    await userEvent.click(screen.getByTestId("ai-chat-send"));

    expect(await screen.findByTestId("ai-chat-error")).toHaveTextContent(
      "Chat request failed."
    );
  });
});
