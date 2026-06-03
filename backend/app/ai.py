from __future__ import annotations

import json
import os

import httpx

from app.ai_board import AIValidationError, validate_operation_shape, validate_operations

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-oss-20b:free"


class AIConfigurationError(Exception):
    pass


class AIRequestError(Exception):
    pass


BOARD_ASSISTANT_JSON_SCHEMA: dict[str, object] = {
    "type": "object",
    "properties": {
        "message": {"type": "string"},
        "operations": {
            "type": "array",
            "items": {
                "anyOf": [
                    {
                        "type": "object",
                        "properties": {
                            "op": {"type": "string", "const": "rename_column"},
                            "column_id": {"type": "string"},
                            "title": {"type": "string"},
                        },
                        "required": ["op", "column_id", "title"],
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "properties": {
                            "op": {"type": "string", "const": "create_card"},
                            "column_id": {"type": "string"},
                            "title": {"type": "string"},
                            "details": {"type": "string"},
                        },
                        "required": ["op", "column_id", "title", "details"],
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "properties": {
                            "op": {"type": "string", "const": "update_card"},
                            "card_id": {"type": "string"},
                            "title": {"type": "string"},
                            "details": {"type": "string"},
                        },
                        "required": ["op", "card_id", "title", "details"],
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "properties": {
                            "op": {"type": "string", "const": "delete_card"},
                            "card_id": {"type": "string"},
                        },
                        "required": ["op", "card_id"],
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "properties": {
                            "op": {"type": "string", "const": "move_card"},
                            "card_id": {"type": "string"},
                            "column_id": {"type": "string"},
                            "position": {"type": "integer"},
                        },
                        "required": ["op", "card_id", "column_id", "position"],
                        "additionalProperties": False,
                    },
                ]
            },
        },
    },
    "required": ["message", "operations"],
    "additionalProperties": False,
}

BOARD_ASSISTANT_SYSTEM_PROMPT = """You are a helpful assistant for a Kanban project board.
You receive the current board JSON (columns with cardIds and a cards map).
Answer the user clearly in the message field.
When they ask for board changes, list operations in the operations array.
Use only existing column_id and card_id values from the board.
For create_card, only column_id, title, and details are required (no card_id).
If no board changes are needed, return an empty operations array.
"""


def openrouter_api_key() -> str | None:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    return key or None


def require_api_key() -> str:
    api_key = openrouter_api_key()
    if not api_key:
        raise AIConfigurationError(
            "OPENROUTER_API_KEY is not set. Add it to the project root .env file."
        )
    return api_key


def build_chat_payload(
    messages: list[dict[str, str]],
    *,
    structured: bool = False,
) -> dict[str, object]:
    payload: dict[str, object] = {
        "model": MODEL,
        "messages": messages,
    }
    if structured:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "board_assistant_response",
                "strict": True,
                "schema": BOARD_ASSISTANT_JSON_SCHEMA,
            },
        }
    return payload


def build_openrouter_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def openrouter_error_detail(error: httpx.HTTPError) -> str:
    if not isinstance(error, httpx.HTTPStatusError):
        return "OpenRouter request failed."

    try:
        body = error.response.json()
        nested = body.get("error")
        if isinstance(nested, dict):
            message = nested.get("message")
            if isinstance(message, str) and message.strip():
                return message.strip()
    except (json.JSONDecodeError, AttributeError, TypeError):
        pass

    return "OpenRouter request failed."


def extract_message_content(response_json: dict) -> str:
    try:
        return response_json["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, AttributeError) as error:
        raise AIRequestError("OpenRouter returned an unexpected response shape.") from error


def _post_chat_completion(
    payload: dict[str, object],
    *,
    client: httpx.Client | None = None,
) -> dict:
    api_key = require_api_key()
    headers = build_openrouter_headers(api_key)

    if client is not None:
        response = client.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    with httpx.Client(timeout=60.0) as http_client:
        response = http_client.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()


def chat_completion(
    messages: list[dict[str, str]],
    *,
    client: httpx.Client | None = None,
) -> str:
    payload = build_chat_payload(messages)
    response_json = _post_chat_completion(payload, client=client)
    return extract_message_content(response_json)


def parse_assistant_json(content: str) -> dict:
    try:
        data = json.loads(content)
    except json.JSONDecodeError as error:
        raise AIRequestError("AI response was not valid JSON.") from error

    if not isinstance(data, dict):
        raise AIRequestError("AI response must be a JSON object.")

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        raise AIRequestError("AI response must include a non-empty message.")

    operations = data.get("operations", [])
    if operations is None:
        operations = []
    if not isinstance(operations, list):
        raise AIRequestError("AI response operations must be an array.")

    normalized_ops: list[dict] = []
    for operation in operations:
        normalized_ops.append(validate_operation_shape(operation))

    return {"message": message.strip(), "operations": normalized_ops}


def build_board_chat_messages(
    board: dict,
    history: list[dict[str, str]],
    user_message: str,
) -> list[dict[str, str]]:
    board_json = json.dumps(board, separators=(",", ":"))
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": f"{BOARD_ASSISTANT_SYSTEM_PROMPT}\n\nCurrent board:\n{board_json}",
        }
    ]
    messages.extend(history)
    messages.append({"role": "user", "content": user_message})
    return messages


def chat_board_assistant(
    board: dict,
    history: list[dict[str, str]],
    user_message: str,
    *,
    client: httpx.Client | None = None,
) -> dict:
    messages = build_board_chat_messages(board, history, user_message)
    payload = build_chat_payload(messages, structured=True)
    response_json = _post_chat_completion(payload, client=client)
    content = extract_message_content(response_json)
    parsed = parse_assistant_json(content)
    parsed["operations"] = validate_operations(board, parsed["operations"])
    return parsed
