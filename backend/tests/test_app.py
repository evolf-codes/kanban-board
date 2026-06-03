from app import main


def test_health_returns_ok(client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_index_returns_static_html(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Project Management MVP" in response.text
    assert "/api/health" in response.text


def test_resolve_frontend_path_returns_exported_asset(
    tmp_path, monkeypatch
) -> None:
    frontend_dir = tmp_path / "frontend"
    asset_dir = frontend_dir / "_next" / "static"
    asset_dir.mkdir(parents=True)
    asset = asset_dir / "app.js"
    asset.write_text("console.log('ok');", encoding="utf-8")
    monkeypatch.setattr(main, "FRONTEND_DIR", frontend_dir)

    assert main.resolve_frontend_path("_next/static/app.js") == asset


def test_resolve_frontend_path_falls_back_to_exported_index(
    tmp_path, monkeypatch
) -> None:
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    index = frontend_dir / "index.html"
    index.write_text("<h1>Kanban Studio</h1>", encoding="utf-8")
    monkeypatch.setattr(main, "FRONTEND_DIR", frontend_dir)

    assert main.resolve_frontend_path("board") == index


def test_resolve_frontend_path_rejects_path_traversal(
    tmp_path, monkeypatch
) -> None:
    frontend_dir = tmp_path / "frontend"
    frontend_dir.mkdir()
    secret = tmp_path / "secret.txt"
    secret.write_text("nope", encoding="utf-8")
    monkeypatch.setattr(main, "FRONTEND_DIR", frontend_dir)

    assert main.resolve_frontend_path("../secret.txt") is None
