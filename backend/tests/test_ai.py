import pytest
from fastapi.testclient import TestClient

from app.ai import (
    AIConfigurationError,
    MODEL,
    OPENROUTER_URL,
    build_chat_payload,
    build_openrouter_headers,
    chat_completion,
    require_api_key,
)
from app.main import app
from tests.conftest import login


def test_require_api_key_raises_when_missing(monkeypatch) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(AIConfigurationError):
        require_api_key()


def test_build_chat_payload_uses_openrouter_model() -> None:
    payload = build_chat_payload([{"role": "user", "content": "2+2"}])

    assert payload == {
        "model": "openai/gpt-oss-20b:free",
        "messages": [{"role": "user", "content": "2+2"}],
    }


def test_chat_completion_sends_openrouter_request(monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": "4"}}]}

    captured: dict = {}

    class FakeClient:
        def post(self, url, json=None, headers=None):
            captured["url"] = url
            captured["json"] = json
            captured["headers"] = headers
            return FakeResponse()

    result = chat_completion(
        [{"role": "user", "content": "2+2"}],
        client=FakeClient(),  # type: ignore[arg-type]
    )

    assert result == "4"
    assert captured["url"] == OPENROUTER_URL
    assert captured["json"]["model"] == MODEL
    assert captured["headers"]["Authorization"] == "Bearer test-key"


def test_ai_test_requires_authentication(client: TestClient) -> None:
    response = client.post("/api/ai/test")

    assert response.status_code == 401


def test_ai_test_returns_configuration_error_without_api_key(
    client: TestClient, monkeypatch
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    login(client)

    response = client.post("/api/ai/test")

    assert response.status_code == 503
    assert "OPENROUTER_API_KEY" in response.json()["detail"]


def test_ai_test_returns_model_response(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")
    login(client)

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict:
            return {"choices": [{"message": {"content": "4"}}]}

    class FakeClient:
        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def post(self, url, json=None, headers=None):
            return FakeResponse()

    monkeypatch.setattr("app.ai.httpx.Client", lambda **kwargs: FakeClient())

    response = client.post("/api/ai/test")

    assert response.status_code == 200
    assert response.json() == {
        "model": MODEL,
        "prompt": "2+2",
        "response": "4",
    }
