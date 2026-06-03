import { apiRequest } from "@/lib/api";
import type { BoardData } from "@/lib/kanban";

export async function fetchBoard(): Promise<BoardData> {
  const board = await apiRequest<BoardData>("/api/board");

  if (!Array.isArray(board.columns) || !board.cards) {
    throw new Error(
      "Invalid board response from API. Rebuild and restart the backend container."
    );
  }

  return board;
}

export async function renameColumn(
  columnId: string,
  title: string
): Promise<BoardData> {
  return apiRequest<BoardData>(`/api/columns/${columnId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });
}

export async function createCard(
  columnId: string,
  title: string,
  details: string
): Promise<BoardData> {
  return apiRequest<BoardData>("/api/cards", {
    method: "POST",
    body: JSON.stringify({ column_id: columnId, title, details }),
  });
}

export async function deleteCard(cardId: string): Promise<BoardData> {
  return apiRequest<BoardData>(`/api/cards/${cardId}`, {
    method: "DELETE",
  });
}

export async function moveCardOnBoard(
  cardId: string,
  columnId: string,
  position: number
): Promise<BoardData> {
  return apiRequest<BoardData>(`/api/cards/${cardId}/move`, {
    method: "PATCH",
    body: JSON.stringify({ column_id: columnId, position }),
  });
}
