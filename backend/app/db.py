from __future__ import annotations

import os
import sqlite3
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BACKEND_DIR / "data" / "pm.db"


def database_path() -> Path:
    override = os.environ.get("DATABASE_PATH")
    if override:
        return Path(override)
    return DEFAULT_DB_PATH


def connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS boards (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'Kanban Studio'
);

CREATE TABLE IF NOT EXISTS columns (
    id TEXT PRIMARY KEY,
    board_id TEXT NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    position INTEGER NOT NULL,
    UNIQUE(board_id, position)
);

CREATE TABLE IF NOT EXISTS cards (
    id TEXT PRIMARY KEY,
    board_id TEXT NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    column_id TEXT NOT NULL REFERENCES columns(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    position INTEGER NOT NULL,
    UNIQUE(column_id, position)
);
"""

SEED_COLUMNS = [
    ("col-backlog", "board-user", "Backlog", 0),
    ("col-discovery", "board-user", "Discovery", 1),
    ("col-progress", "board-user", "In Progress", 2),
    ("col-review", "board-user", "Review", 3),
    ("col-done", "board-user", "Done", 4),
]

SEED_CARDS = [
    (
        "card-1",
        "board-user",
        "col-backlog",
        "Align roadmap themes",
        "Draft quarterly themes with impact statements and metrics.",
        0,
    ),
    (
        "card-2",
        "board-user",
        "col-backlog",
        "Gather customer signals",
        "Review support tags, sales notes, and churn feedback.",
        1,
    ),
    (
        "card-3",
        "board-user",
        "col-discovery",
        "Prototype analytics view",
        "Sketch initial dashboard layout and key drill-downs.",
        0,
    ),
    (
        "card-4",
        "board-user",
        "col-progress",
        "Refine status language",
        "Standardize column labels and tone across the board.",
        0,
    ),
    (
        "card-5",
        "board-user",
        "col-progress",
        "Design card layout",
        "Add hierarchy and spacing for scanning dense lists.",
        1,
    ),
    (
        "card-6",
        "board-user",
        "col-review",
        "QA micro-interactions",
        "Verify hover, focus, and loading states.",
        0,
    ),
    (
        "card-7",
        "board-user",
        "col-done",
        "Ship marketing page",
        "Final copy approved and asset pack delivered.",
        0,
    ),
    (
        "card-8",
        "board-user",
        "col-done",
        "Close onboarding sprint",
        "Document release notes and share internally.",
        1,
    ),
]


def init_db() -> None:
    with connect() as connection:
        connection.executescript(SCHEMA_SQL)
        user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        if user_count == 0:
            connection.execute(
                "INSERT INTO users (id, username) VALUES (1, 'user')"
            )
            connection.execute(
                "INSERT INTO boards (id, user_id, title) VALUES ('board-user', 1, 'Kanban Studio')"
            )
            connection.executemany(
                "INSERT INTO columns (id, board_id, title, position) VALUES (?, ?, ?, ?)",
                SEED_COLUMNS,
            )
            connection.executemany(
                """
                INSERT INTO cards (id, board_id, column_id, title, details, position)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                SEED_CARDS,
            )
        connection.commit()
