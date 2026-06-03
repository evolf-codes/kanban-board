from __future__ import annotations

from app.board_store import (
    create_card,
    delete_card,
    move_card,
    mutate_board,
    rename_column,
    update_card,
)

ALLOWED_OPS = frozenset(
    {"rename_column", "create_card", "update_card", "delete_card", "move_card"}
)


class AIValidationError(Exception):
    pass


def _column_ids(board: dict) -> set[str]:
    return {column["id"] for column in board["columns"]}


def _card_ids(board: dict) -> set[str]:
    return set(board["cards"].keys())


def validate_operation_shape(operation: object) -> dict:
    if not isinstance(operation, dict):
        raise AIValidationError("Each operation must be an object.")

    op_type = operation.get("op")
    if op_type not in ALLOWED_OPS:
        raise AIValidationError(f"Unsupported operation: {op_type!r}.")

    if op_type == "rename_column":
        column_id = operation.get("column_id")
        title = operation.get("title")
        if not isinstance(column_id, str) or not column_id:
            raise AIValidationError("rename_column requires column_id.")
        if not isinstance(title, str) or not title.strip():
            raise AIValidationError("rename_column requires a non-empty title.")
        return {"op": op_type, "column_id": column_id, "title": title.strip()}

    if op_type == "create_card":
        column_id = operation.get("column_id")
        title = operation.get("title")
        details = operation.get("details", "")
        if not isinstance(column_id, str) or not column_id:
            raise AIValidationError("create_card requires column_id.")
        if not isinstance(title, str) or not title.strip():
            raise AIValidationError("create_card requires a non-empty title.")
        if details is None:
            details = ""
        if not isinstance(details, str):
            raise AIValidationError("create_card details must be a string.")
        return {
            "op": op_type,
            "column_id": column_id,
            "title": title.strip(),
            "details": details,
        }

    if op_type == "update_card":
        card_id = operation.get("card_id")
        title = operation.get("title")
        details = operation.get("details", "")
        if not isinstance(card_id, str) or not card_id:
            raise AIValidationError("update_card requires card_id.")
        if not isinstance(title, str) or not title.strip():
            raise AIValidationError("update_card requires a non-empty title.")
        if details is None:
            details = ""
        if not isinstance(details, str):
            raise AIValidationError("update_card details must be a string.")
        return {
            "op": op_type,
            "card_id": card_id,
            "title": title.strip(),
            "details": details,
        }

    if op_type == "delete_card":
        card_id = operation.get("card_id")
        if not isinstance(card_id, str) or not card_id:
            raise AIValidationError("delete_card requires card_id.")
        return {"op": op_type, "card_id": card_id}

    card_id = operation.get("card_id")
    column_id = operation.get("column_id")
    position = operation.get("position")
    if not isinstance(card_id, str) or not card_id:
        raise AIValidationError("move_card requires card_id.")
    if not isinstance(column_id, str) or not column_id:
        raise AIValidationError("move_card requires column_id.")
    if not isinstance(position, int) or isinstance(position, bool) or position < 0:
        raise AIValidationError("move_card requires a non-negative integer position.")
    return {
        "op": op_type,
        "card_id": card_id,
        "column_id": column_id,
        "position": position,
    }


def validate_operations(board: dict, operations: list) -> list[dict]:
    if not isinstance(operations, list):
        raise AIValidationError("operations must be an array.")

    column_ids = _column_ids(board)
    card_ids = _card_ids(board)
    validated: list[dict] = []

    for operation in operations:
        op = validate_operation_shape(operation)
        if op["op"] in {"rename_column", "create_card", "move_card"}:
            if op["column_id"] not in column_ids:
                raise AIValidationError(f"Unknown column_id: {op['column_id']}.")
        if op["op"] in {"update_card", "delete_card", "move_card"}:
            if op["card_id"] not in card_ids:
                raise AIValidationError(f"Unknown card_id: {op['card_id']}.")
        validated.append(op)

    return validated


def _apply_operation(connection, board_id: str, operation: dict) -> None:
    op_type = operation["op"]
    if op_type == "rename_column":
        rename_column(connection, board_id, operation["column_id"], operation["title"])
        return
    if op_type == "create_card":
        create_card(
            connection,
            board_id,
            operation["column_id"],
            operation["title"],
            operation["details"],
        )
        return
    if op_type == "update_card":
        update_card(
            connection,
            board_id,
            operation["card_id"],
            operation["title"],
            operation["details"],
        )
        return
    if op_type == "delete_card":
        delete_card(connection, board_id, operation["card_id"])
        return
    move_card(
        connection,
        board_id,
        operation["card_id"],
        operation["column_id"],
        operation["position"],
    )


def apply_operations(username: str, operations: list[dict]) -> dict:
    def handler(connection, board_id: str) -> None:
        for operation in operations:
            _apply_operation(connection, board_id, operation)

    return mutate_board(username, handler)
