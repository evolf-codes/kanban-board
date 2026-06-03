def test_api_index_returns_json(client) -> None:
    response = client.get("/api")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "/api/health" in response.json()["health"]


def test_login_success_sets_session(client) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )

    assert response.status_code == 200
    assert response.json() == {"username": "user"}

    session = client.get("/api/auth/session")
    assert session.status_code == 200
    assert session.json() == {"authenticated": True, "username": "user"}


def test_login_failure_does_not_set_session(client) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "wrong"},
    )

    assert response.status_code == 401

    session = client.get("/api/auth/session")
    assert session.json() == {"authenticated": False, "username": None}


def test_logout_clears_session(client) -> None:
    client.post(
        "/api/auth/login",
        json={"username": "user", "password": "password"},
    )

    logout = client.post("/api/auth/logout")
    assert logout.status_code == 200
    assert logout.json() == {"ok": True}

    session = client.get("/api/auth/session")
    assert session.json() == {"authenticated": False, "username": None}


def test_board_requires_authentication(client) -> None:
    response = client.get("/api/board")

    assert response.status_code == 401


def test_board_allows_authenticated_user(client) -> None:
    from tests.conftest import login as login_user

    login_user(client)

    response = client.get("/api/board")
    board = response.json()

    assert response.status_code == 200
    assert "columns" in board
    assert "cards" in board
    assert len(board["columns"]) == 5
