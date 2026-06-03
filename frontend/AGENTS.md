# Frontend Guide

## Current App

The frontend is a Next.js App Router demo for the Kanban board. It currently runs as a frontend-only app with client-side state and will later be statically built and served by the FastAPI backend.

## Important Files

- `src/app/page.tsx` renders the board page.
- `src/app/layout.tsx` defines the app shell and fonts.
- `src/app/globals.css` defines Tailwind CSS setup and project color variables.
- `src/components/KanbanBoard.tsx` owns the current board state and drag-and-drop behavior.
- `src/components/KanbanColumn.tsx` renders one board column and column rename controls.
- `src/components/KanbanCard.tsx` renders an editable/deletable card.
- `src/components/NewCardForm.tsx` handles adding a card to a column.
- `src/components/KanbanCardPreview.tsx` renders the drag overlay preview.
- `src/lib/kanban.ts` contains the board types, demo data, ID creation, and card movement logic.

## Current Data Model

The UI uses `BoardData` from `src/lib/kanban.ts`:

- `columns`: ordered list of fixed columns.
- `cards`: card lookup by card ID.
- Each column stores ordered `cardIds`.
- Cards have `id`, `title`, and `details`.

Future backend API responses should preserve this shape where practical, even though the database will use normalized SQLite tables.

## Auth and API

- `src/lib/auth.ts` calls `/api/auth/session`, `/api/auth/login`, and `/api/auth/logout` with cookies.
- `src/lib/board-api.ts` loads and mutates the board through `/api/board` and related routes.
- `src/lib/ai-api.ts` sends chat messages to `POST /api/ai/chat`.
- `src/components/AiChatSidebar.tsx` is the AI chat panel beside the board.
- `src/lib/api.ts` contains shared JSON fetch helpers.
- `src/components/AppGate.tsx` shows login or the board based on session state.
- `src/components/LoginForm.tsx` handles dummy sign in.
- During `next dev`, `/api/*` requests are proxied to the FastAPI backend on port 8000.

## UI Behavior

- The board starts from `initialData`.
- Columns can be renamed.
- Cards can be added and deleted.
- Cards can be moved within and across columns with `@dnd-kit`.
- The current app does not persist changes after refresh.
- The app uses project colors from `AGENTS.md` through CSS variables in `globals.css`.

## Testing

Use the existing scripts from `package.json`:

- `npm run lint`
- `npm run test:unit`
- `npm run test:e2e`
- `npm run test:all`

Vitest covers component and library behavior. Playwright covers browser-level Kanban behavior.

## Implementation Notes

- Keep the frontend simple and close to the existing component structure.
- Prefer small API helper functions when wiring the board to FastAPI.
- Preserve the existing board interactions while adding backend persistence.
- UI changes are acceptable when they improve the MVP user experience.
- Do not add extra product features beyond sign in, persistent Kanban, and AI chat.
- The AI sidebar keeps conversation history in component state and refreshes the board when `boardUpdated` is true.
