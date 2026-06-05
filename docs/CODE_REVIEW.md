# Code Review

Review date: 2026-06-05
Reviewer: Senior Engineer
Scope: Full codebase (backend, frontend, Docker, scripts, tests)

## Test Status (before and after)

| Suite | Count | Status |
|-------|-------|--------|
| Backend unit tests | 46 | All pass |
| Frontend unit tests | 21 | All pass |
| Frontend lint | -- | Clean |
| TypeScript (`tsc --noEmit`) | -- | Clean (was 200+ errors) |

## Issues Fixed

### 1. Missing `"use client"` directives on three components

**Files:** `src/components/KanbanCard.tsx`, `src/components/KanbanColumn.tsx`, `src/components/NewCardForm.tsx`

**Problem:** These components use React hooks (`useSortable`, `useDroppable`, `useState`) but were not marked with `"use client"`. While they worked because parent `KanbanBoard.tsx` is a client component, this is fragile -- importing them from a server component would crash at runtime. Next.js 16 enforces this boundary more strictly.

**Fix:** Added `"use client"` at the top of each file.

### 2. Vitest globals type reference was wrong

**File:** `src/test/vitest.d.ts`

**Problem:** The triple-slash directive referenced `vitest` instead of `vitest/globals`. The main `vitest` types do not include the global test functions (`vi`, `describe`, `it`, `expect`). This caused 200+ false TypeScript errors in every test file, making `tsc --noEmit` unusable.

**Fix:** Changed `/// <reference types="vitest" />` to `/// <reference types="vitest/globals" />`. All TypeScript errors resolved.

### 3. Unnecessary default card details text

**File:** `backend/app/board_store.py:138`

**Problem:** When creating a card with empty details, the code defaulted to `"No details yet."`:
```python
details or "No details yet."
```
This text appeared in the UI for every new card created from the AI sidebar without details. It is an unnecessary opinion -- the user can add details later or leave them blank.

**Fix:** Removed the fallback. Empty string is used when no details are provided.

### 4. Duplicate `httpx` in dependency groups

**File:** `backend/pyproject.toml`

**Problem:** `httpx` appeared in both runtime `dependencies` and the `dev` dependency group. It is already listed as a runtime dependency (used by the AI client at runtime), so the dev entry was redundant.

**Fix:** Removed `httpx` from the dev dependency group.

## Issues Noted (no fix needed)

| Observation | Rationale |
|-------------|-----------|
| `.env` is not tracked by git | Verified with `git ls-files`. No API key exposure. |
| `ChatMessage` role field does not validate `system` role | The schema only accepts `"user"` or `"assistant"`. The `system` prompt is injected server-side, not by the client. Intentional. |
| Double validation of AI operations in `ai_routes.py` | `chat_board_assistant()` validates against the board, then `ai_chat()` validates again before applying. Redundant but harmless defense-in-depth. |
| Frontend `KanbanBoard` optimistically updates before API | Valid pattern. On failure, the board is reloaded from the server. |
| `_apply_column_order` uses negative-then-positive positions | Necessary to avoid UNIQUE(column_id, position) constraint violations during reordering. Correct and intentional. |
| No `Content-Type` header set in static file catch-all | `FileResponse` auto-detects MIME types via `mimetypes.guess_type`. JS, CSS, HTML all resolve correctly. |
| `output: "export"` with `rewrites` in `next.config.ts` | Rewrites are only used during `next dev` (proxied to FastAPI). Static export ignores them. Correct for the architecture -- FastAPI serves the static files directly. |
| Old Python 3.9 on host | Project requires 3.12 but tests run under 3.9 with `from __future__ import annotations`. Docker uses 3.12 in production. |
