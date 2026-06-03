from __future__ import annotations

import os

from fastapi import Depends, HTTPException, Request
from pydantic import BaseModel

VALID_USERNAME = "user"
VALID_PASSWORD = "password"


class LoginRequest(BaseModel):
    username: str
    password: str


def session_secret() -> str:
    return os.environ.get("SESSION_SECRET", "dev-session-secret")


def verify_credentials(username: str, password: str) -> bool:
    return username == VALID_USERNAME and password == VALID_PASSWORD


def get_current_user(request: Request) -> str:
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


def get_optional_user(request: Request) -> str | None:
    return request.session.get("user")
