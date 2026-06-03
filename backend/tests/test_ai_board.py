import json

import pytest

from app.ai import parse_assistant_json
from app.ai_board import AIValidationError, apply_operations, validate_operations
from app.board_store import read_board
from tests.conftest import login


def test_parse_assistant_json_accepts_response_only() -> None:
    parsed = parse_assistant_json(
        json.dumps({"message": "Hello", "operations": []})
    )

    assert parsed == {"message": "Hello", "operations": []}


def test_parse_assistant_json_rejects_invalid_json() -> None:
    with pytest.raises(Exception):
        parse_assistant_json("not json")


def test_validate_operations_rejects_unknown_column(client) -> None:
    login(client)
    board = read_board("user")

    with pytest.raises(AIValidationError, match="Unknown column_id"):
        validate_operations(
            board,
            [{"op": "rename_column", "column_id": "missing", "title": "X"}],
        )


def test_validate_operations_rejects_unknown_card(client) -> None:
    login(client)
    board = read_board("user")

    with pytest.raises(AIValidationError, match="Unknown card_id"):
        validate_operations(
            board,
            [{"op": "delete_card", "card_id": "missing"}],
        )


def test_apply_rename_column(client) -> None:
    login(client)
    board = read_board("user")
    operations = validate_operations(
        board,
        [{"op": "rename_column", "column_id": "col-backlog", "title": "Ideas"}],
    )

    updated = apply_operations("user", operations)

    assert updated["columns"][0]["title"] == "Ideas"


def test_apply_create_card(client) -> None:
    login(client)
    board = read_board("user")
    operations = validate_operations(
        board,
        [
            {
                "op": "create_card",
                "column_id": "col-review",
                "title": "AI card",
                "details": "From AI",
            }
        ],
    )

    updated = apply_operations("user", operations)
    review = next(column for column in updated["columns"] if column["id"] == "col-review")
    new_id = review["cardIds"][-1]

    assert updated["cards"][new_id]["title"] == "AI card"


def test_apply_update_card(client) -> None:
    login(client)
    board = read_board("user")
    operations = validate_operations(
        board,
        [
            {
                "op": "update_card",
                "card_id": "card-1",
                "title": "New title",
                "details": "New details",
            }
        ],
    )

    updated = apply_operations("user", operations)

    assert updated["cards"]["card-1"]["title"] == "New title"
    assert updated["cards"]["card-1"]["details"] == "New details"


def test_apply_delete_card(client) -> None:
    login(client)
    board = read_board("user")
    operations = validate_operations(
        board,
        [{"op": "delete_card", "card_id": "card-1"}],
    )

    updated = apply_operations("user", operations)

    assert "card-1" not in updated["cards"]
    assert "card-1" not in updated["columns"][0]["cardIds"]


def test_apply_move_card(client) -> None:
    login(client)
    board = read_board("user")
    operations = validate_operations(
        board,
        [
            {
                "op": "move_card",
                "card_id": "card-1",
                "column_id": "col-done",
                "position": 0,
            }
        ],
    )

    updated = apply_operations("user", operations)
    done = next(column for column in updated["columns"] if column["id"] == "col-done")

    assert done["cardIds"][0] == "card-1"


def test_invalid_operations_do_not_change_board(client) -> None:
    login(client)
    before = client.get("/api/board").json()

    with pytest.raises(AIValidationError):
        validate_operations(
            before,
            [{"op": "delete_card", "card_id": "card-missing"}],
        )

    after = client.get("/api/board").json()
    assert after == before
