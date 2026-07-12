import re
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from app.services.comments_store import CommentsStore

router = APIRouter()

RATE_LIMIT_SECONDS = 30
_last_submission: dict[str, float] = {}

_store = CommentsStore()

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def get_store() -> CommentsStore:
    return _store


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


class CommentIn(BaseModel):
    name: str = Field(..., max_length=100)
    email: str = Field(..., max_length=200)
    body: str = Field(..., max_length=2000)

    @field_validator("name", "email", "body")
    @classmethod
    def not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("must not be empty")
        return v

    @field_validator("email")
    @classmethod
    def valid_email_shape(cls, v: str) -> str:
        if not _EMAIL_RE.match(v):
            raise ValueError("must be a valid email address")
        return v


class CommentOut(BaseModel):
    id: int
    name: str
    body: str
    created_at: str


@router.post("/comments", status_code=201, response_model=CommentOut)
def create_comment(
    payload: CommentIn,
    request: Request,
    store: CommentsStore = Depends(get_store),
) -> dict:
    client_ip = _client_ip(request)
    now = time.time()
    last = _last_submission.get(client_ip)
    if last is not None and now - last < RATE_LIMIT_SECONDS:
        raise HTTPException(status_code=429, detail="Please wait before commenting again.")

    try:
        comment = store.insert_comment(payload.name, payload.email, payload.body)
    except Exception:
        raise HTTPException(status_code=500, detail="Could not save comment.")

    _last_submission[client_ip] = now
    return comment


@router.get("/comments", response_model=list[CommentOut])
def get_comments(store: CommentsStore = Depends(get_store)) -> list[dict]:
    return store.list_comments()
