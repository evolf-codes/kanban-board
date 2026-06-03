"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { sendChat, type ChatMessage } from "@/lib/ai-api";
import type { BoardData } from "@/lib/kanban";

type AiChatSidebarProps = {
  onBoardUpdate: (board: BoardData) => void;
  disabled?: boolean;
};

export const AiChatSidebar = ({
  onBoardUpdate,
  disabled = false,
}: AiChatSidebarProps) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const node = scrollRef.current;
    if (!node) {
      return;
    }

    if (typeof node.scrollTo === "function") {
      node.scrollTo({ top: node.scrollHeight, behavior: "smooth" });
      return;
    }

    node.scrollTop = node.scrollHeight;
  }, [messages, pending]);

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const text = draft.trim();
    if (!text || pending || disabled) {
      return;
    }

    setDraft("");
    setError(null);
    setPending(true);

    const history = messages;

    try {
      const response = await sendChat(text, history);
      setMessages((current) => [
        ...current,
        { role: "user", content: text },
        { role: "assistant", content: response.message },
      ]);

      if (response.boardUpdated && response.board) {
        onBoardUpdate(response.board);
      }
    } catch (chatError) {
      setError(
        chatError instanceof Error
          ? chatError.message
          : "Unable to reach the assistant."
      );
    } finally {
      setPending(false);
    }
  };

  return (
    <aside
      className="flex w-full flex-col border-t border-[var(--stroke)] bg-white/90 backdrop-blur lg:h-screen lg:max-h-screen lg:w-[min(380px,34vw)] lg:border-l lg:border-t-0"
      data-testid="ai-chat-sidebar"
    >
      <header className="border-b border-[var(--stroke)] px-5 py-5">
        <p className="text-xs font-semibold uppercase tracking-[0.3em] text-[var(--gray-text)]">
          AI Assistant
        </p>
        <h2 className="mt-2 font-display text-xl font-semibold text-[var(--navy-dark)]">
          Board helper
        </h2>
        <p className="mt-2 text-sm leading-6 text-[var(--gray-text)]">
          Ask questions or request card and column changes. Updates apply
          automatically when the assistant confirms them.
        </p>
      </header>

      <div
        ref={scrollRef}
        className="flex min-h-[220px] flex-1 flex-col gap-3 overflow-y-auto px-5 py-4 lg:min-h-0"
        data-testid="ai-chat-messages"
      >
        {messages.length === 0 ? (
          <p className="text-sm text-[var(--gray-text)]">
            Try &quot;What cards are in review?&quot; or &quot;Rename backlog to
            Ideas.&quot;
          </p>
        ) : null}

        {messages.map((message, index) => (
          <div
            key={`${message.role}-${index}-${message.content.slice(0, 24)}`}
            className={
              message.role === "user"
                ? "ml-6 rounded-2xl rounded-tr-md bg-[var(--primary-blue)] px-4 py-3 text-sm text-white"
                : "mr-4 rounded-2xl rounded-tl-md border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm leading-6 text-[var(--navy-dark)]"
            }
            data-testid={
              message.role === "user" ? "ai-chat-message-user" : "ai-chat-message-assistant"
            }
          >
            {message.content}
          </div>
        ))}

        {pending ? (
          <p
            className="text-sm text-[var(--gray-text)]"
            data-testid="ai-chat-pending"
          >
            Assistant is thinking...
          </p>
        ) : null}
      </div>

      {error ? (
        <p
          className="mx-5 mb-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          role="alert"
          data-testid="ai-chat-error"
        >
          {error}
        </p>
      ) : null}

      <form
        className="border-t border-[var(--stroke)] px-5 py-4"
        onSubmit={(event) => void handleSubmit(event)}
      >
        <label className="sr-only" htmlFor="ai-chat-input">
          Message the assistant
        </label>
        <textarea
          id="ai-chat-input"
          className="min-h-[88px] w-full resize-y rounded-xl border border-[var(--stroke)] bg-white px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
          data-testid="ai-chat-input"
          disabled={pending || disabled}
          placeholder="Ask about the board or request a change..."
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              void handleSubmit(event);
            }
          }}
        />
        <button
          className="mt-3 w-full rounded-xl bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-60"
          data-testid="ai-chat-send"
          disabled={pending || disabled || !draft.trim()}
          type="submit"
        >
          {pending ? "Sending..." : "Send"}
        </button>
      </form>
    </aside>
  );
};
