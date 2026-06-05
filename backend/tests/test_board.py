from tests.conftest import login

SEED_COLUMN_IDS = [
    "col-backlog",
    "col-discovery",
    "col-progress",
    "col-review",
    "col-done",
]


def test_board_requires_authentication(client) -> None:
    response = client.get("/api/board")

    assert response.status_code == 401


def test_board_returns_seed_data(client) -> None:
    login(client)

    response = client.get("/api/board")
    board = response.json()

    assert response.status_code == 200
    assert [column["id"] for column in board["columns"]] == SEED_COLUMN_IDS
    assert board["columns"][0]["cardIds"] == ["card-1", "card-2"]
    assert board["cards"]["card-1"]["title"] == "Align roadmap themes"


def test_rename_column_persists(client) -> None:
    login(client)

    response = client.patch(
        "/api/columns/col-backlog",
        json={"title": "Ideas"},
    )
    board = response.json()

    assert response.status_code == 200
    assert board["columns"][0]["title"] == "Ideas"

    reload = client.get("/api/board").json()
    assert reload["columns"][0]["title"] == "Ideas"


def test_create_card_adds_to_column(client) -> None:
    login(client)

    response = client.post(
        "/api/cards",
        json={
            "column_id": "col-review",
            "title": "New card",
            "details": "Notes",
        },
    )
    board = response.json()

    assert response.status_code == 200
    review = next(column for column in board["columns"] if column["id"] == "col-review")
    new_card_id = review["cardIds"][-1]
    assert board["cards"][new_card_id]["title"] == "New card"


def test_update_card_persists(client) -> None:
    login(client)

    response = client.patch(
        "/api/cards/card-1",
        json={"title": "Updated title", "details": "Updated details"},
    )
    board = response.json()

    assert response.status_code == 200
    assert board["cards"]["card-1"]["title"] == "Updated title"
    assert board["cards"]["card-1"]["details"] == "Updated details"


def test_delete_card_renumbers_column(client) -> None:
    login(client)

    response = client.delete("/api/cards/card-1")
    board = response.json()

    assert response.status_code == 200
    backlog = board["columns"][0]
    assert "card-1" not in backlog["cardIds"]
    assert backlog["cardIds"] == ["card-2"]


def test_move_card_within_column(client) -> None:
    login(client)

    response = client.patch(
        "/api/cards/card-1/move",
        json={"column_id": "col-backlog", "position": 1},
    )
    board = response.json()

    assert response.status_code == 200
    assert board["columns"][0]["cardIds"] == ["card-2", "card-1"]


def test_move_card_between_columns(client) -> None:
    login(client)

    response = client.patch(
        "/api/cards/card-1/move",
        json={"column_id": "col-review", "position": 0},
    )
    board = response.json()

    assert response.status_code == 200
    assert "card-1" not in board["columns"][0]["cardIds"]
    review = next(column for column in board["columns"] if column["id"] == "col-review")
    assert review["cardIds"][0] == "card-1"


def test_unknown_column_returns_404(client) -> None:
    login(client)

    response = client.patch(
        "/api/columns/missing-column",
        json={"title": "Nope"},
    )

    assert response.status_code == 404


def test_unknown_card_returns_404(client) -> None:
    login(client)

    response = client.delete("/api/cards/missing-card")

    assert response.status_code == 404


def test_move_card_to_empty_column(client) -> None:
    login(client)

    board = client.get("/api/board").json()
    discovery = next(column for column in board["columns"] if column["id"] == "col-discovery")
    assert discovery["cardIds"] == ["card-3"]

    response = client.patch(
        "/api/cards/card-3/move",
        json={"column_id": "col-backlog", "position": 0},
    )
    assert response.status_code == 200

    discovery = client.get("/api/board").json()["columns"][1]
    assert discovery["cardIds"] == []

    response = client.patch(
        "/api/cards/card-1/move",
        json={"column_id": "col-discovery", "position": 0},
    )
    board = response.json()
    discovery = next(column for column in board["columns"] if column["id"] == "col-discovery")
    assert discovery["cardIds"] == ["card-1"]
