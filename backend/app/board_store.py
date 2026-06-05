from __future__ import annotations

import secrets
import sqlite3

from app.db import connect


class BoardNotFoundError(Exception):
    pass


class ColumnNotFoundError(Exception):
    pass


class CardNotFoundError(Exception):
    pass


def get_board_id(connection: sqlite3.Connection, username: str) -> str:
    row = connection.execute(
        """
        SELECT boards.id
        FROM boards
        JOIN users ON users.id = boards.user_id
        WHERE users.username = ?
        """,
        (username,),
    ).fetchone()
    if row is None:
        raise BoardNotFoundError(username)
    return row["id"]


def load_board_data(connection: sqlite3.Connection, board_id: str) -> dict:
    columns = connection.execute(
        """
        SELECT id, title
        FROM columns
        WHERE board_id = ?
        ORDER BY position ASC
        """,
        (board_id,),
    ).fetchall()

    cards = connection.execute(
        """
        SELECT id, column_id, title, details, position
        FROM cards
        WHERE board_id = ?
        ORDER BY column_id ASC, position ASC
        """,
        (board_id,),
    ).fetchall()

    cards_by_column: dict[str, list[str]] = {column["id"]: [] for column in columns}
    card_map: dict[str, dict[str, str]] = {}

    for card in cards:
        cards_by_column[card["column_id"]].append(card["id"])
        card_map[card["id"]] = {
            "id": card["id"],
            "title": card["title"],
            "details": card["details"],
        }

    return {
        "columns": [
            {
                "id": column["id"],
                "title": column["title"],
                "cardIds": cards_by_column[column["id"]],
            }
            for column in columns
        ],
        "cards": card_map,
    }


def rename_column(
    connection: sqlite3.Connection, board_id: str, column_id: str, title: str
) -> None:
    result = connection.execute(
        """
        UPDATE columns
        SET title = ?
        WHERE id = ? AND board_id = ?
        """,
        (title, column_id, board_id),
    )
    if result.rowcount == 0:
        raise ColumnNotFoundError(column_id)


def _renumber_column(connection: sqlite3.Connection, column_id: str, board_id: str) -> None:
    rows = connection.execute(
        """
        SELECT id
        FROM cards
        WHERE column_id = ? AND board_id = ?
        ORDER BY position ASC, id ASC
        """,
        (column_id, board_id),
    ).fetchall()
    for index, row in enumerate(rows):
        connection.execute(
            "UPDATE cards SET position = ? WHERE id = ? AND board_id = ?",
            (index, row["id"], board_id),
        )


def create_card(
    connection: sqlite3.Connection,
    board_id: str,
    column_id: str,
    title: str,
    details: str,
) -> str:
    column = connection.execute(
        "SELECT id FROM columns WHERE id = ? AND board_id = ?",
        (column_id, board_id),
    ).fetchone()
    if column is None:
        raise ColumnNotFoundError(column_id)

    next_position = connection.execute(
        "SELECT COALESCE(MAX(position), -1) + 1 FROM cards WHERE column_id = ?",
        (column_id,),
    ).fetchone()[0]

    card_id = f"card-{secrets.token_hex(4)}"
    connection.execute(
        """
        INSERT INTO cards (id, board_id, column_id, title, details, position)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (card_id, board_id, column_id, title, details, next_position),
    )
    return card_id


def update_card(
    connection: sqlite3.Connection,
    board_id: str,
    card_id: str,
    title: str,
    details: str,
) -> None:
    result = connection.execute(
        """
        UPDATE cards
        SET title = ?, details = ?
        WHERE id = ? AND board_id = ?
        """,
        (title, details, card_id, board_id),
    )
    if result.rowcount == 0:
        raise CardNotFoundError(card_id)


def delete_card(connection: sqlite3.Connection, board_id: str, card_id: str) -> None:
    row = connection.execute(
        "SELECT column_id FROM cards WHERE id = ? AND board_id = ?",
        (card_id, board_id),
    ).fetchone()
    if row is None:
        raise CardNotFoundError(card_id)

    connection.execute("DELETE FROM cards WHERE id = ?", (card_id,))
    _renumber_column(connection, row["column_id"], board_id)


def _ordered_card_ids(
    connection: sqlite3.Connection, board_id: str, column_id: str
) -> list[str]:
    return [
        row["id"]
        for row in connection.execute(
            """
            SELECT id
            FROM cards
            WHERE column_id = ? AND board_id = ?
            ORDER BY position ASC, id ASC
            """,
            (column_id, board_id),
        ).fetchall()
    ]


def _apply_column_order(
    connection: sqlite3.Connection,
    board_id: str,
    column_id: str,
    ordered_ids: list[str],
) -> None:
    for index, current_id in enumerate(ordered_ids):
        connection.execute(
            """
            UPDATE cards
            SET position = ?
            WHERE id = ? AND board_id = ?
            """,
            (-index - 1, current_id, board_id),
        )

    for index, current_id in enumerate(ordered_ids):
        connection.execute(
            """
            UPDATE cards
            SET column_id = ?, position = ?
            WHERE id = ? AND board_id = ?
            """,
            (column_id, index, current_id, board_id),
        )


def move_card(
    connection: sqlite3.Connection,
    board_id: str,
    card_id: str,
    column_id: str,
    position: int,
) -> None:
    card = connection.execute(
        "SELECT column_id FROM cards WHERE id = ? AND board_id = ?",
        (card_id, board_id),
    ).fetchone()
    if card is None:
        raise CardNotFoundError(card_id)

    target_column = connection.execute(
        "SELECT id FROM columns WHERE id = ? AND board_id = ?",
        (column_id, board_id),
    ).fetchone()
    if target_column is None:
        raise ColumnNotFoundError(column_id)

    source_column_id = card["column_id"]
    source_ids = _ordered_card_ids(connection, board_id, source_column_id)

    if card_id not in source_ids:
        raise CardNotFoundError(card_id)

    source_ids.remove(card_id)

    if source_column_id == column_id:
        position = max(0, min(position, len(source_ids)))
        source_ids.insert(position, card_id)
        _apply_column_order(connection, board_id, column_id, source_ids)
        return

    connection.execute(
        """
        UPDATE cards
        SET column_id = ?, position = -1
        WHERE id = ? AND board_id = ?
        """,
        (column_id, card_id, board_id),
    )
    _apply_column_order(connection, board_id, source_column_id, source_ids)

    target_ids = _ordered_card_ids(connection, board_id, column_id)
    target_ids.remove(card_id)
    position = max(0, min(position, len(target_ids)))
    target_ids.insert(position, card_id)
    _apply_column_order(connection, board_id, column_id, target_ids)


def read_board(username: str) -> dict:
    with connect() as connection:
        board_id = get_board_id(connection, username)
        return load_board_data(connection, board_id)


def mutate_board(username: str, handler) -> dict:
    with connect() as connection:
        try:
            board_id = get_board_id(connection, username)
            handler(connection, board_id)
            board_data = load_board_data(connection, board_id)
            connection.commit()
            return board_data
        except Exception:
            connection.rollback()
            raise
