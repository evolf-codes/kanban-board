from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from app.auth import (
    LoginRequest,
    get_optional_user,
    session_secret,
    verify_credentials,
)
from app.ai_routes import router as ai_router
from app.board_routes import router as board_router
from app.db import init_db

APP_DIR = Path(__file__).resolve().parent
FALLBACK_STATIC_DIR = APP_DIR / "static"
FRONTEND_DIR = APP_DIR / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Project Management MVP", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=session_secret())

api = APIRouter(prefix="/api")


@api.get("")
def api_index():
    return {
        "health": "/api/health",
        "session": "/api/auth/session",
        "login": "/api/auth/login",
        "logout": "/api/auth/logout",
        "board": "/api/board",
        "columns": "/api/columns/{column_id}",
        "cards": "/api/cards",
        "ai_test": "/api/ai/test",
        "ai_chat": "/api/ai/chat",
    }


@api.get("/health")
def health():
    return {"status": "ok"}


@api.post("/auth/login")
def login(payload: LoginRequest, request: Request):
    if not verify_credentials(payload.username, payload.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    request.session["user"] = payload.username
    return {"username": payload.username}


@api.post("/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


@api.get("/auth/session")
def session(request: Request):
    user = get_optional_user(request)
    return {"authenticated": user is not None, "username": user}


api.include_router(board_router)
api.include_router(ai_router)
app.include_router(api)


@app.get("/", response_class=HTMLResponse)
def index():
    frontend_index = FRONTEND_DIR / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index)

    return (FALLBACK_STATIC_DIR / "index.html").read_text(encoding="utf-8")


def resolve_frontend_path(path: str) -> Path | None:
    if path.startswith("api") or path.startswith("api/"):
        return None

    requested_path = (FRONTEND_DIR / path).resolve()
    if FRONTEND_DIR in requested_path.parents and requested_path.is_file():
        return requested_path

    frontend_index = FRONTEND_DIR / "index.html"
    if frontend_index.exists():
        return frontend_index

    return None


@app.get("/{path:path}")
def frontend_asset_or_route(path: str):
    if path.startswith("api") or path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")

    frontend_path = resolve_frontend_path(path)
    if frontend_path:
        return FileResponse(frontend_path)

    raise HTTPException(status_code=404, detail="Not found")
