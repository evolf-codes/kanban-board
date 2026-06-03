from pathlib import Path

from app.db import SEED_CARDS, connect, database_path, init_db


def test_database_file_is_created(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "created.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_file))

    init_db()

    assert db_file.exists()


def test_seed_data_inserts_once(tmp_path, monkeypatch) -> None:
    db_file = tmp_path / "seed.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_file))

    init_db()
    init_db()

    with connect() as connection:
        user_count = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        card_count = connection.execute("SELECT COUNT(*) FROM cards").fetchone()[0]

    assert user_count == 1
    assert card_count == len(SEED_CARDS)


def test_default_database_path_points_to_backend_data(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_PATH", raising=False)
    path = database_path()
    assert path.name == "pm.db"
    assert path.parent.name == "data"
