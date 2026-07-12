import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api import comments as comments_api
from app.services.comments_store import CommentsStore


@pytest.fixture
def client(tmp_path):
    test_store = CommentsStore(tmp_path / "test_comments.db")
    app.dependency_overrides[comments_api.get_store] = lambda: test_store
    comments_api._last_submission.clear()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_valid_submission_returns_201_without_email(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "Great tool!"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Jane"
    assert data["body"] == "Great tool!"
    assert "email" not in data
    assert "id" in data
    assert "created_at" in data


def test_missing_field_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com"},
    )

    assert response.status_code == 422


def test_blank_field_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "   ", "email": "jane@example.com", "body": "Great tool!"},
    )

    assert response.status_code == 422


def test_malformed_email_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "not-an-email", "body": "Great tool!"},
    )

    assert response.status_code == 422


def test_body_too_long_returns_422(client):
    response = client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "x" * 2001},
    )

    assert response.status_code == 422


def test_rapid_repeat_submission_returns_429(client):
    payload = {"name": "Jane", "email": "jane@example.com", "body": "Great tool!"}

    first = client.post("/comments", json=payload)
    second = client.post("/comments", json=payload)

    assert first.status_code == 201
    assert second.status_code == 429


def test_different_forwarded_ips_are_not_rate_limited_against_each_other(client):
    payload = {"name": "Jane", "email": "jane@example.com", "body": "Great tool!"}

    first = client.post("/comments", json=payload, headers={"X-Forwarded-For": "1.2.3.4"})
    second = client.post("/comments", json=payload, headers={"X-Forwarded-For": "5.6.7.8"})

    assert first.status_code == 201
    assert second.status_code == 201


def test_same_forwarded_ip_rapid_repeat_returns_429(client):
    payload = {"name": "Jane", "email": "jane@example.com", "body": "Great tool!"}

    first = client.post("/comments", json=payload, headers={"X-Forwarded-For": "9.9.9.9"})
    second = client.post("/comments", json=payload, headers={"X-Forwarded-For": "9.9.9.9"})

    assert first.status_code == 201
    assert second.status_code == 429


def test_get_comments_never_includes_email(client):
    client.post(
        "/comments",
        json={"name": "Jane", "email": "jane@example.com", "body": "Nice!"},
    )

    response = client.get("/comments")

    assert response.status_code == 200
    comments = response.json()
    assert len(comments) == 1
    assert "email" not in comments[0]
    assert comments[0]["name"] == "Jane"
