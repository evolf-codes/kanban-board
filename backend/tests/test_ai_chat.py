import json

from fastapi.testclient import TestClient

from app.ai import build_chat_payload
from tests.conftest import login


def test_structured_payload_includes_json_schema() -> None:
    payload = build_chat_payload([{"role": "user", "content": "hi"}], structured=True)

    assert payload["response_format"]["type"] == "json_schema"
    assert payload["response_format"]["json_schema"]["strict"] is True


def test_chat_requires_authentication(client: TestClient) -> None:
    response = client.post(
        "/api/ai/chat",
        json={"message": "Hello", "history": []},
    )

    assert response.status_code == 401


def test_chat_response_only(client: TestClient, monkeypatch) -> None:
    login(client)

    def fake_chat(board, history, user_message, *, client=None):
        del board, history, user_message, client
        return {"message": "No changes needed.", "operations": []}

    monkeypatch.setattr("app.ai_routes.chat_board_assistant", fake_chat)

    response = client.post(
        "/api/ai/chat",
        json={"message": "What columns do I have?", "history": []},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["message"] == "No changes needed."
    assert body["boardUpdated"] is False
    assert body["board"] is None


def test_chat_applies_board_updates(client: TestClient, monkeypatch) -> None:
    login(client)

    def fake_chat(board, history, user_message, *, client=None):
        del history, user_message, client
        return {
            "message": "Renamed the backlog column.",
            "operations": [
                {"op": "rename_column", "column_id": "col-backlog", "title": "Ideas"}
            ],
        }

    monkeypatch.setattr("app.ai_routes.chat_board_assistant", fake_chat)

    response = client.post(
        "/api/ai/chat",
        json={"message": "Rename backlog to Ideas", "history": []},
    )
    body = response.json()

    assert response.status_code == 200
    assert body["boardUpdated"] is True
    assert body["board"]["columns"][0]["title"] == "Ideas"


def test_chat_rejects_invalid_ai_output(client: TestClient, monkeypatch) -> None:
    login(client)
    before = client.get("/api/board").json()

    def fake_chat(board, history, user_message, *, client=None):
        del board, history, user_message, client
        return {
            "message": "Deleting a card.",
            "operations": [{"op": "delete_card", "card_id": "card-missing"}],
        }

    monkeypatch.setattr("app.ai_routes.chat_board_assistant", fake_chat)

    response = client.post(
        "/api/ai/chat",
        json={"message": "Delete missing card", "history": []},
    )

    assert response.status_code == 422
    assert client.get("/api/board").json() == before


def test_chat_passes_history_to_assistant(client: TestClient, monkeypatch) -> None:
    login(client)
    captured: dict = {}

    def fake_chat(board, history, user_message, *, client=None):
        captured["history"] = history
        captured["message"] = user_message
        del board, client
        return {"message": "OK", "operations": []}

    monkeypatch.setattr("app.ai_routes.chat_board_assistant", fake_chat)

    client.post(
        "/api/ai/chat",
        json={
            "message": "Next question",
            "history": [
                {"role": "user", "content": "First"},
                {"role": "assistant", "content": "Reply"},
            ],
        },
    )

    assert captured["message"] == "Next question"
    assert captured["history"] == [
        {"role": "user", "content": "First"},
        {"role": "assistant", "content": "Reply"},
    ]
