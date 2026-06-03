from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.auth import get_current_user
from app.board_store import (
    BoardNotFoundError,
    CardNotFoundError,
    ColumnNotFoundError,
    create_card,
    delete_card,
    move_card,
    mutate_board,
    read_board,
    rename_column,
    update_card,
)
from app.schemas import (
    CardCreateRequest,
    CardMoveRequest,
    CardUpdateRequest,
    ColumnRenameRequest,
)

router = APIRouter()


def _handle_store_error(error: Exception) -> None:
    if isinstance(error, BoardNotFoundError):
        raise HTTPException(status_code=404, detail="Board not found") from error
    if isinstance(error, ColumnNotFoundError):
        raise HTTPException(status_code=404, detail="Column not found") from error
    if isinstance(error, CardNotFoundError):
        raise HTTPException(status_code=404, detail="Card not found") from error
    raise error


@router.get("/board")
def get_board(user: str = Depends(get_current_user)):
    try:
        return read_board(user)
    except BoardNotFoundError as error:
        _handle_store_error(error)


@router.patch("/columns/{column_id}")
def patch_column(
    column_id: str,
    payload: ColumnRenameRequest,
    user: str = Depends(get_current_user),
):
    try:
        return mutate_board(
            user,
            lambda connection, board_id: rename_column(
                connection, board_id, column_id, payload.title
            ),
        )
    except (BoardNotFoundError, ColumnNotFoundError) as error:
        _handle_store_error(error)


@router.post("/cards")
def post_card(payload: CardCreateRequest, user: str = Depends(get_current_user)):
    try:
        return mutate_board(
            user,
            lambda connection, board_id: create_card(
                connection,
                board_id,
                payload.column_id,
                payload.title,
                payload.details,
            ),
        )
    except (BoardNotFoundError, ColumnNotFoundError) as error:
        _handle_store_error(error)


@router.patch("/cards/{card_id}")
def patch_card(
    card_id: str,
    payload: CardUpdateRequest,
    user: str = Depends(get_current_user),
):
    try:
        return mutate_board(
            user,
            lambda connection, board_id: update_card(
                connection,
                board_id,
                card_id,
                payload.title,
                payload.details,
            ),
        )
    except (BoardNotFoundError, CardNotFoundError) as error:
        _handle_store_error(error)


@router.delete("/cards/{card_id}")
def remove_card(card_id: str, user: str = Depends(get_current_user)):
    try:
        return mutate_board(
            user,
            lambda connection, board_id: delete_card(connection, board_id, card_id),
        )
    except (BoardNotFoundError, CardNotFoundError) as error:
        _handle_store_error(error)


@router.patch("/cards/{card_id}/move")
def patch_card_move(
    card_id: str,
    payload: CardMoveRequest,
    user: str = Depends(get_current_user),
):
    try:
        return mutate_board(
            user,
            lambda connection, board_id: move_card(
                connection,
                board_id,
                card_id,
                payload.column_id,
                payload.position,
            ),
        )
    except (BoardNotFoundError, ColumnNotFoundError, CardNotFoundError) as error:
        _handle_store_error(error)
