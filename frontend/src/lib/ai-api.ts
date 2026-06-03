import { readJson } from "@/lib/api";
import type { BoardData } from "@/lib/kanban";

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatResponse = {
  message: string;
  boardUpdated: boolean;
  board: BoardData | null;
};

async function chatErrorMessage(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string };
    if (typeof body.detail === "string" && body.detail.trim()) {
      return body.detail;
    }
  } catch {
    // ignore parse errors
  }

  if (response.status === 503) {
    return "AI is not configured. Add OPENROUTER_API_KEY to .env and restart.";
  }

  return "Chat request failed.";
}

export async function sendChat(
  message: string,
  history: ChatMessage[]
): Promise<ChatResponse> {
  let response: Response;

  try {
    response = await fetch("/api/ai/chat", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, history }),
    });
  } catch {
    throw new Error(
      "Cannot reach the API. Use http://localhost:8000 after running ./scripts/start.sh."
    );
  }

  if (!response.ok) {
    throw new Error(await chatErrorMessage(response));
  }

  return readJson<ChatResponse>(response);
}
