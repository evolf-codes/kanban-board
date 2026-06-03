# Backend Guide

## Current Backend

The backend is a FastAPI app served from `backend/app/main.py`. It currently provides the Part 2 scaffold:

- `GET /` returns static hello world HTML from `backend/app/static/index.html`.
- `GET /api/health` returns `{"status": "ok"}`.
- `POST /api/auth/login`, `POST /api/auth/logout`, and `GET /api/auth/session` manage dummy session auth.
- `GET /api/board` returns persisted `BoardData` JSON for the signed-in user.
- `PATCH /api/columns/{column_id}`, `POST /api/cards`, `PATCH /api/cards/{card_id}`, `DELETE /api/cards/{card_id}`, and `PATCH /api/cards/{card_id}/move` mutate the SQLite board.
- SQLite lives at `backend/data/pm.db` (override with `DATABASE_PATH`).
- `POST /api/ai/test` calls OpenRouter with a `2+2` prompt (requires sign-in and `OPENROUTER_API_KEY`).
- `POST /api/ai/chat` sends the user message, optional history, and current board to OpenRouter with Structured Outputs; valid operations are applied to SQLite.

## AI

- Client code lives in `app/ai.py`.
- Uses model `openai/gpt-oss-20b:free` through the OpenRouter chat completions API.
- Read `OPENROUTER_API_KEY` from the environment (loaded from project root `.env` in Docker).

## Python Tooling

Use `uv` for Python dependency management.

Common commands:

- `uv sync`
- `uv run pytest`
- `uv run uvicorn app.main:app --reload`

## Testing

Backend tests live in `backend/tests/`. Keep tests focused on API behavior and persistence rules as the backend grows.

## Implementation Notes

- Keep route handlers small and move shared behavior into modules as needed.
- Database schema and API shape are documented in `docs/DATABASE.md`. Implement only after user approval.
- Do not read secrets directly from committed files. Use environment variables.