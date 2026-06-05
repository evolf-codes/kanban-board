# Kanban PM MVP

## Architecture

- **Frontend**: Next.js App Router (`frontend/`), static export served by FastAPI.
- **Backend**: Python FastAPI (`backend/`), SQLite, session auth.
- **AI**: OpenRouter (`openai/gpt-oss-20b:free`), Structured Outputs, `OPENROUTER_API_KEY` in `.env`.
- **Docker**: Multi-stage build (Node 24 → Python 3.12-slim), `docker compose up --build`, port 8000.

## Two run modes

| Mode | Command | URL | API proxy |
|------|---------|-----|-----------|
| Docker (full stack) | `./scripts/start.sh` | `http://localhost:8000` | Built-in (FastAPI serves frontend) |
| Frontend dev only | `cd frontend && npm run dev` | `http://localhost:3000` | `next.config.ts` rewrites `/api/*` to `http://127.0.0.1:8000` |

Backend dev: `cd backend && uv run uvicorn app.main:app --reload` (port 8000).

## Auth

Hardcoded credentials: `user` / `password`. Session-based (cookie). Login required for all `/api/board` and `/api/ai/*` routes.

## Commands

```sh
# Frontend
cd frontend
npm run lint            # ESLint flat config (eslint-config-next)
npx tsc --noEmit        # TypeScript check
npm run test:unit       # Vitest (jsdom, @/ path alias)
npm run test:e2e        # Playwright (starts backend:8001 + frontend:3000, fresh SQLite)
npm run test:all        # unit + e2e

# Backend
cd backend
uv run pytest           # 47 tests, autouse fixture creates temp SQLite per test
uv run uvicorn app.main:app --reload
```

Recommended order: `npm run lint && npx tsc --noEmit && npm run test:unit`.

## Key facts

- All backend route handlers are synchronous (`def`, not `async def`).
- `DATABASE_PATH` env var overrides SQLite location (default `backend/data/pm.db`). Playwright uses `/tmp/pm-playwright.db`.
- `uv` is the Python package manager. Docker installs via `curl ... | sh`. On macOS host: `python3 -m uv <command>`.
- Python 3.12+ required (Docker). Host may be older — `from __future__ import annotations` in every file avoids `str | None` syntax errors.
- Board data shape (shared frontend/backend): `BoardData { columns: Column[]; cards: Record<string, Card> }`. Backend normalizes to SQLite, reconstructs on read.
- Colors in CSS variables: `--accent-yellow: #ecad0a`, `--primary-blue: #209dd7`, `--secondary-purple: #753991`, `--navy-dark: #032147`, `--gray-text: #888888`.
- Drag-and-drop uses `@dnd-kit` with custom collision detection (`pointerWithin` → `closestCenter`). Column-background drops insert at position 0.
- AI sidebar refreshes board when response has `boardUpdated: true`.
- `.env` and `backend/data/*.db` are gitignored.
- Subdirectory AGENTS.md files: `backend/AGENTS.md`, `frontend/AGENTS.md`, `scripts/AGENTS.md`.

## Coding standards

1. Never over-engineer. No unnecessary defensive programming. No extra features.
2. No emojis anywhere in code or docs.
3. When debugging: identify root cause with evidence before fixing. Do not guess.
4. Keep it simple — match existing code style and library choices.