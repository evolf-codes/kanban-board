import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { KanbanBoard } from "@/components/KanbanBoard";
import * as boardApi from "@/lib/board-api";
import { initialData } from "@/lib/kanban";

vi.mock("@/lib/board-api", () => ({
  fetchBoard: vi.fn(),
  renameColumn: vi.fn(),
  createCard: vi.fn(),
  deleteCard: vi.fn(),
  moveCardOnBoard: vi.fn(),
}));

const boardProps = {
  username: "user",
  onLogout: async () => undefined,
};

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

describe("KanbanBoard", () => {
  beforeEach(() => {
    vi.mocked(boardApi.fetchBoard).mockResolvedValue(initialData);
    vi.mocked(boardApi.renameColumn).mockImplementation(async (columnId, title) => ({
      ...initialData,
      columns: initialData.columns.map((column) =>
        column.id === columnId ? { ...column, title } : column
      ),
    }));
    vi.mocked(boardApi.createCard).mockImplementation(async (columnId, title, details) => {
      const id = "card-new";
      return {
        ...initialData,
        cards: {
          ...initialData.cards,
          [id]: { id, title, details },
        },
        columns: initialData.columns.map((column) =>
          column.id === columnId
            ? { ...column, cardIds: [...column.cardIds, id] }
            : column
        ),
      };
    });
    vi.mocked(boardApi.deleteCard).mockImplementation(async (cardId) => ({
      ...initialData,
      cards: Object.fromEntries(
        Object.entries(initialData.cards).filter(([id]) => id !== cardId)
      ),
      columns: initialData.columns.map((column) => ({
        ...column,
        cardIds: column.cardIds.filter((id) => id !== cardId),
      })),
    }));
    vi.mocked(boardApi.moveCardOnBoard).mockResolvedValue(initialData);
  });

  it("renders five columns after loading", async () => {
    render(<KanbanBoard {...boardProps} />);

    await waitFor(() => {
      expect(screen.getAllByTestId(/column-/i)).toHaveLength(5);
    });
  });

  it("renames a column on blur", async () => {
    render(<KanbanBoard {...boardProps} />);
    await waitFor(() => expect(screen.getAllByTestId(/column-/i)).toHaveLength(5));

    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    await userEvent.tab();

    expect(boardApi.renameColumn).toHaveBeenCalledWith("col-backlog", "New Name");
  });

  it("adds and removes a card through the API", async () => {
    render(<KanbanBoard {...boardProps} />);
    await waitFor(() => expect(screen.getAllByTestId(/column-/i)).toHaveLength(5));

    const column = getFirstColumn();
    await userEvent.click(
      within(column).getByRole("button", { name: /add a card/i })
    );

    await userEvent.type(
      within(column).getByPlaceholderText(/card title/i),
      "New card"
    );
    await userEvent.type(within(column).getByPlaceholderText(/details/i), "Notes");
    await userEvent.click(
      within(column).getByRole("button", { name: /add card/i })
    );

    expect(boardApi.createCard).toHaveBeenCalledWith(
      "col-backlog",
      "New card",
      "Notes"
    );
    expect(await within(column).findByText("New card")).toBeInTheDocument();

    await userEvent.click(
      within(column).getByRole("button", { name: "Delete New card" })
    );

    expect(boardApi.deleteCard).toHaveBeenCalledWith("card-new");
  });
});
