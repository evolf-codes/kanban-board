# Project Management MVP

## Run Locally

Mac or Linux:

```bash
./scripts/start.sh
```

Windows PowerShell:

```powershell
.\scripts\start.ps1
```

Windows Command Prompt:

```bat
scripts\start.bat
```

Open `http://localhost:8000` for the Kanban app (not port 3000). Sign in with username `user` and password `password`.

API endpoints live under `/api`, for example `http://localhost:8000/api/health` and `http://localhost:8000/api/auth/session`. Visiting `http://localhost:8000/api` returns a JSON index of routes.

After code changes, restart with `./scripts/stop.sh` then `./scripts/start.sh` so Docker rebuilds the image.

The Kanban board loads from `GET /api/board` and saves changes through the board API routes.

## AI (OpenRouter)

Copy `.env.example` to `.env` in the project root and set `OPENROUTER_API_KEY`.

After signing in, test connectivity:

```bash
curl -b cookies.txt -c cookies.txt -X POST http://localhost:8000/api/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"user","password":"password"}'

curl -b cookies.txt -X POST http://localhost:8000/api/ai/test
```

Chat with board context (returns `message`, `boardUpdated`, and `board` when the AI applies changes):

```bash
curl -b cookies.txt -X POST http://localhost:8000/api/ai/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Rename the backlog column to Ideas","history":[]}'
```

After sign-in, the Kanban page includes an AI chat sidebar on the right (stacked below the board on narrow screens).

The Docker build exports the Next.js frontend and serves it from FastAPI at `/`.

## Stop

Mac or Linux:

```bash
./scripts/stop.sh
```

Windows PowerShell:

```powershell
.\scripts\stop.ps1
```

Windows Command Prompt:

```bat
scripts\stop.bat
```

## Backend Tests

```bash
cd backend
uv sync
uv run pytest
```

## Frontend Tests

```bash
cd frontend
npm run test:unit
npm run test:e2e
```
