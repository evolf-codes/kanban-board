from __future__ import annotations

import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.ai import (
    AIConfigurationError,
    AIRequestError,
    MODEL,
    chat_board_assistant,
    chat_completion,
    openrouter_error_detail,
)
from app.ai_board import AIValidationError, apply_operations, validate_operations
from app.ai_schemas import ChatRequest
from app.auth import get_current_user
from app.board_store import read_board

router = APIRouter(prefix="/ai", tags=["ai"])

MATH_TEST_PROMPT = "What is 2+2? Reply with only the number."


def _ai_http_error(error: Exception) -> HTTPException:
    if isinstance(error, AIConfigurationError):
        return HTTPException(status_code=503, detail=str(error))
    if isinstance(error, (AIRequestError, AIValidationError)):
        return HTTPException(status_code=422, detail=str(error))
    if isinstance(error, httpx.HTTPError):
        return HTTPException(status_code=502, detail=openrouter_error_detail(error))
    raise error


@router.post("/test")
def ai_test(user: str = Depends(get_current_user)):
    del user

    try:
        response = chat_completion([{"role": "user", "content": MATH_TEST_PROMPT}])
    except (AIConfigurationError, AIRequestError, httpx.HTTPError) as error:
        raise _ai_http_error(error) from error

    return {
        "model": MODEL,
        "prompt": "2+2",
        "response": response,
    }


@router.post("/chat")
def ai_chat(payload: ChatRequest, user: str = Depends(get_current_user)):
    board = read_board(user)
    history = [
        {"role": message.role, "content": message.content} for message in payload.history
    ]

    try:
        assistant = chat_board_assistant(board, history, payload.message)
    except (AIConfigurationError, AIRequestError, AIValidationError, httpx.HTTPError) as error:
        raise _ai_http_error(error) from error

    operations = assistant["operations"]
    board_updated = len(operations) > 0
    refreshed_board = None

    if board_updated:
        try:
            validate_operations(board, operations)
            refreshed_board = apply_operations(user, operations)
        except AIValidationError as error:
            raise _ai_http_error(error) from error

    return {
        "message": assistant["message"],
        "boardUpdated": board_updated,
        "board": refreshed_board,
    }
