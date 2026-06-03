# Database Design

This document defines the normalized SQLite schema for the Kanban MVP, seed data, constraints, and the JSON shape the API will return to the frontend.

## Goals

- Support multiple users in the schema while the MVP enforces one board per user.
- Persist column order, card order within columns, and card fields (`title`, `details`).
- Keep five fixed columns per board; columns can be renamed but not created or deleted.
- Match the existing frontend `BoardData` type in `frontend/src/lib/kanban.ts`.

## SQLite File

- Path: `backend/data/pm.db` (created on first startup if missing).
- Access: stdlib `sqlite3` from the FastAPI backend.
- No ORM for the MVP; use plain SQL and small helper functions.

## Tables

### `users`

Stores application users. MVP auth still checks hardcoded credentials, but rows exist for future real authentication.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT |
| `username` | TEXT | NOT NULL, UNIQUE |

### `boards`

One board per user for the MVP.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | TEXT | PRIMARY KEY |
| `user_id` | INTEGER | NOT NULL, UNIQUE, REFERENCES `users(id)` ON DELETE CASCADE |
| `title` | TEXT | NOT NULL DEFAULT 'Kanban Studio' |

`UNIQUE(user_id)` enforces one board per user.

### `columns`

Fixed workflow columns on a board. Column set is seeded once; the API will not support create/delete for MVP.

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | TEXT | PRIMARY KEY |
| `board_id` | TEXT | NOT NULL, REFERENCES `boards(id)` ON DELETE CASCADE |
| `title` | TEXT | NOT NULL |
| `position` | INTEGER | NOT NULL |

Constraints:

- `UNIQUE(board_id, position)` keeps a stable column order.
- `UNIQUE(board_id, id)` is implied by primary key on `id` scoped per board via application logic.

Allowed mutation in MVP: `UPDATE title` only.

### `cards`

Cards belong to a board and sit in one column at a time. `position` is the sort order within that column (0-based).

| Column | Type | Constraints |
|--------|------|-------------|
| `id` | TEXT | PRIMARY KEY |
| `board_id` | TEXT | NOT NULL, REFERENCES `boards(id)` ON DELETE CASCADE |
| `column_id` | TEXT | NOT NULL, REFERENCES `columns(id)` ON DELETE CASCADE |
| `title` | TEXT | NOT NULL |
| `details` | TEXT | NOT NULL DEFAULT '' |
| `position` | INTEGER | NOT NULL |

Constraints:

- `UNIQUE(column_id, position)` keeps card order within a column.
- Application code must renumber positions when a card is moved, inserted, or deleted.

Allowed mutations in MVP: insert, update `title`/`details`, update `column_id` + `position` (move), delete.

## Entity Relationships

```mermaid
erDiagram
    users ||--o| boards : owns
    boards ||--|{ columns : has
    boards ||--|{ cards : has
    columns ||--|{ cards : contains

    users {
        int id PK
        text username UK
    }
    boards {
        text id PK
        int user_id UK FK
        text title
    }
    columns {
        text id PK
        text board_id FK
        text title
        int position
    }
    cards {
        text id PK
        text board_id FK
        text column_id FK
        text title
        text details
        int position
    }
```

## MVP Rules

| Rule | How it is enforced |
|------|-------------------|
| One board per user | `boards.user_id` UNIQUE |
| Five fixed columns | Seed only; API rejects column create/delete |
| Column rename | `UPDATE columns SET title = ? WHERE id = ? AND board_id = ?` |
| Card ordering | `cards.position` per `column_id`; renumber on move/add/delete |
| User isolation | All queries filter by authenticated `users.username` joined to `boards` |

## Seed Data

On first database creation, seed one user, one board, five columns, and eight cards using the same IDs and content as `initialData` in `frontend/src/lib/kanban.ts`.

### User

| id | username |
|----|----------|
| 1 | user |

### Board

| id | user_id | title |
|----|---------|-------|
| board-user | 1 | Kanban Studio |

### Columns

| id | board_id | title | position |
|----|----------|-------|----------|
| col-backlog | board-user | Backlog | 0 |
| col-discovery | board-user | Discovery | 1 |
| col-progress | board-user | In Progress | 2 |
| col-review | board-user | Review | 3 |
| col-done | board-user | Done | 4 |

### Cards

| id | board_id | column_id | title | details | position |
|----|----------|-----------|-------|---------|----------|
| card-1 | board-user | col-backlog | Align roadmap themes | Draft quarterly themes with impact statements and metrics. | 0 |
| card-2 | board-user | col-backlog | Gather customer signals | Review support tags, sales notes, and churn feedback. | 1 |
| card-3 | board-user | col-discovery | Prototype analytics view | Sketch initial dashboard layout and key drill-downs. | 0 |
| card-4 | board-user | col-progress | Refine status language | Standardize column labels and tone across the board. | 0 |
| card-5 | board-user | col-progress | Design card layout | Add hierarchy and spacing for scanning dense lists. | 1 |
| card-6 | board-user | col-review | QA micro-interactions | Verify hover, focus, and loading states. | 0 |
| card-7 | board-user | col-done | Ship marketing page | Final copy approved and asset pack delivered. | 0 |
| card-8 | board-user | col-done | Close onboarding sprint | Document release notes and share internally. | 1 |

## API JSON Shape

`GET /api/board` returns the authenticated user's board in the same shape as frontend `BoardData`:

```json
{
  "columns": [
    {
      "id": "col-backlog",
      "title": "Backlog",
      "cardIds": ["card-1", "card-2"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Align roadmap themes",
      "details": "Draft quarterly themes with impact statements and metrics."
    }
  }
}
```

Mapping rules:

- `columns` is ordered by `columns.position` ascending.
- Each column's `cardIds` lists card IDs in `cards.position` order for that column.
- `cards` is a map keyed by card ID for O(1) lookup in the UI.

## Planned API Mutations (Part 6 and 7)

| Operation | Method | Route | Persistence |
|-----------|--------|-------|-------------|
| Read board | GET | `/api/board` | Load full `BoardData` JSON |
| Rename column | PATCH | `/api/columns/{column_id}` | `UPDATE columns.title` |
| Create card | POST | `/api/cards` | `INSERT` + assign `position` at end of column |
| Update card | PATCH | `/api/cards/{card_id}` | `UPDATE title, details` |
| Delete card | DELETE | `/api/cards/{card_id}` | `DELETE` + renumber column positions |
| Move card | PATCH | `/api/cards/{card_id}/move` | `UPDATE column_id, position` + renumber affected columns |

All routes require an authenticated session and must scope rows to the current user's board.

## Initialization

1. Create tables if they do not exist (single SQL script or ordered `CREATE TABLE IF NOT EXISTS` statements).
2. If `users` is empty, run seed inserts inside a transaction.
3. Use the same DB file path in Docker via a volume or `backend/data/` inside the container.

## Planned Tests (Part 6)

- Database file is created when missing.
- Seed data inserts exactly once.
- `GET /api/board` returns JSON matching the seed `BoardData` shape for user `user`.
- Column rename updates only `title`.
- Card create/update/delete/move maintain valid `position` ordering.
- Requests for another user's board data are not accessible (only one MVP user today, but queries must join through `users`).

## Approval

Confirm this schema and API shape before Part 6 implementation. Reply to approve or request changes.
