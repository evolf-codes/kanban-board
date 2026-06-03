# Project Plan

This plan turns the existing frontend-only Kanban demo into a local Dockerized MVP with a FastAPI backend, normalized SQLite persistence, session-cookie sign in, and an OpenRouter-backed AI sidebar that can directly update the board.

## Approved Decisions

- Store Kanban data in normalized SQLite tables, not as a JSON blob.
- Use dummy credentials of `user` and `password`.
- Use a backend-issued session cookie for sign in.
- Allow validated AI Structured Outputs to directly apply Kanban updates.
- Improve the UI when it creates a better user experience, while staying focused on the MVP.

## Part 1: Planning

### Checklist

- [x] Expand this plan into implementation steps with tests and success criteria.
- [x] Create `frontend/AGENTS.md` documenting the existing frontend.
- [ ] Get user approval before starting implementation work.

### Tests

- Documentation-only step. No automated tests required.

### Success Criteria

- The plan is detailed enough for an agent to execute step by step.
- Open implementation decisions are documented.
- The frontend structure and conventions are captured for future agents.

## Part 2: Scaffolding

### Checklist

- [x] Create `backend/` with a minimal FastAPI application.
- [x] Add Python project configuration using `uv`.
- [x] Add a health endpoint such as `GET /api/health`.
- [x] Serve simple static HTML at `/` from FastAPI to prove static serving works.
- [x] Add Docker infrastructure for running the backend locally.
- [x] Add start and stop scripts for Mac, Linux, and Windows in `scripts/`.
- [x] Document the local run flow in the root README or docs with minimal wording.

### Tests

- [x] Backend unit test for `GET /api/health`.
- [ ] Script or manual smoke test confirming Docker starts the app.
- [ ] Smoke test confirming `/` returns HTML and `/api/health` returns JSON.

### Success Criteria

- A new developer can start the app locally with the appropriate script.
- The app runs inside Docker.
- FastAPI can serve both static content and API responses.

## Part 3: Serve the Existing Frontend

### Checklist

- [x] Configure the Next.js frontend for static export if needed.
- [x] Add a build step that produces static frontend assets.
- [x] Update FastAPI to serve the built frontend at `/`.
- [x] Keep the existing Kanban board visible at `/`.
- [x] Preserve current drag-and-drop, add-card, delete-card, and rename-column behavior.
- [x] Ensure Docker builds or copies the frontend assets correctly.

### Tests

- [x] Run frontend unit tests with `npm run test:unit`.
- [x] Run frontend end-to-end tests with `npm run test:e2e`.
- [x] Add or update backend/static-serving tests where practical.
- [ ] Run a Docker smoke test for the served frontend.

### Success Criteria

- Visiting `/` in the Dockerized app displays the Kanban board.
- Existing frontend behavior still works.
- Static frontend assets are served by FastAPI, not a separate Next dev server.

## Part 4: Sign In and Sign Out

### Checklist

- [x] Add backend login and logout routes.
- [x] Accept only the dummy credentials `user` and `password`.
- [x] Issue a simple secure session cookie after successful login.
- [x] Add a current-session route for the frontend to determine auth state.
- [x] Protect the Kanban route or board API access behind the session.
- [x] Add a login screen before the board is shown.
- [x] Add logout behavior that clears the session and returns to login.

### Tests

- [x] Backend tests for successful login, failed login, logout, and current-session behavior.
- [x] Frontend unit tests for login state where useful.
- [x] End-to-end tests for login, viewing the board, and logout.

### Success Criteria

- A user must sign in before seeing the Kanban board.
- Invalid credentials do not create a session.
- Logout removes access until signing in again.

## Part 5: Database Modeling

### Checklist

- [x] Propose a normalized SQLite schema in `docs/`.
- [x] Include tables for users, boards, columns, cards, and card ordering.
- [x] Include the default seed data for the MVP user and board.
- [x] Define constraints needed to keep one board per user for the MVP.
- [x] Define how fixed columns can be renamed without allowing column creation or deletion.
- [x] Define the API JSON shape the frontend will consume.
- [x] Get user sign-off before implementing the schema.

### Tests

- Documentation-only until approved.
- Include planned backend tests for migrations, seed data, and CRUD behavior.

### Success Criteria

- The schema supports multiple users later while keeping one board per user now.
- Card movement, card edits, card creation, card deletion, and column renames are represented cleanly.
- The documented JSON API shape maps clearly to the current frontend `BoardData` model.

## Part 6: Persistent Backend API

### Checklist

- [x] Add SQLite database initialization that creates the database if missing.
- [x] Implement the approved normalized schema.
- [x] Seed the default user, board, columns, and cards when needed.
- [x] Add authenticated API routes to read the current user's board.
- [x] Add authenticated API routes to rename columns.
- [x] Add authenticated API routes to create, edit, delete, and move cards.
- [x] Keep board update operations transactional.
- [x] Return board data in the documented JSON shape.

### Tests

- [x] Backend unit tests for database initialization and seed data.
- [x] Backend API tests for board read and every board mutation.
- [x] Backend tests for unauthorized access.
- [x] Backend tests for card ordering after moves within and across columns.

### Success Criteria

- The backend creates a working SQLite database automatically.
- All board operations persist across app restarts.
- API behavior is covered by focused tests.

## Part 7: Frontend and Backend Integration

### Checklist

- [x] Replace client-only initial board state with API loading.
- [x] Add frontend API helpers for auth and board operations.
- [x] Persist card creation, editing, deletion, movement, and column renames through the backend.
- [x] Add loading and error states that are clear but minimal.
- [x] Refresh or update local state after successful mutations.
- [x] Keep drag-and-drop interactions responsive.

### Tests

- [x] Frontend unit tests for API helper behavior where practical.
- [x] Component tests for loading, errors, and successful board rendering.
- [x] End-to-end tests proving persistence after reload.
- [x] End-to-end tests for card and column mutations through the UI.

### Success Criteria

- The board shown in the UI comes from SQLite through FastAPI.
- Changes made in the UI persist after refresh and restart.
- The frontend remains simple and understandable.

## Part 8: AI Connectivity

### Checklist

- [x] Add OpenRouter configuration using `OPENROUTER_API_KEY` from `.env`.
- [x] Use the `openai/gpt-oss-20b:free` model.
- [x] Add a backend AI client module.
- [x] Add a protected test endpoint or backend test path that sends a simple `2+2` prompt.
- [x] Handle missing API key with a clear startup or request error.

### Tests

- [x] Unit tests for AI client request construction with network calls mocked.
- [x] Manual connectivity test confirming a `2+2` response from OpenRouter.

### Success Criteria

- The backend can successfully call OpenRouter from the local Docker environment.
- The API key is read from environment configuration and is not committed.
- Network-dependent tests are not required for the normal automated suite.

## Part 9: AI Board Updates

### Checklist

- [x] Add a chat API route that accepts the user's message and conversation history.
- [x] Load the authenticated user's current board before calling the AI.
- [x] Send the board JSON, user message, and conversation history to OpenRouter.
- [x] Require Structured Outputs containing a user-facing response and optional board update operations.
- [x] Validate AI output before applying changes.
- [x] Directly apply valid AI updates to the normalized SQLite data.
- [x] Return the assistant response plus the refreshed board when changes occur.

### Tests

- [x] Unit tests for Structured Output validation.
- [x] Backend tests for applying each supported AI board operation.
- [x] Backend tests proving invalid AI updates are rejected without changing the board.
- [x] Mocked chat route tests for response-only and response-plus-update cases.

### Success Criteria

- AI responses can create, edit, delete, and move cards, and rename columns through validated operations.
- Invalid or malformed AI output cannot corrupt board data.
- The frontend can tell when the board changed and refresh accordingly.

## Part 10: AI Sidebar UI

### Checklist

- [x] Add a polished AI chat sidebar to the Kanban page.
- [x] Support conversation history in the UI.
- [x] Send user messages to the backend chat route.
- [x] Render assistant responses clearly.
- [x] Automatically refresh the board when the AI applies updates.
- [x] Add clear pending and error states.
- [x] Keep the layout usable on desktop and smaller screens.

### Tests

- [x] Component tests for the chat sidebar.
- [x] End-to-end tests for sending a chat message and rendering a response with mocked AI behavior.
- [x] End-to-end tests for an AI-triggered board update refreshing the UI.

### Success Criteria

- A signed-in user can chat with the AI from the sidebar.
- The AI can directly update the Kanban board when its Structured Output validates.
- Board updates triggered by AI appear in the UI without a manual page refresh.