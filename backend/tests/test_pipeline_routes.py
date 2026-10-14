import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import pipeline_routes
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.db.database import get_db
from app.db.models import SalaryPost
from app.ingestion.orchestrator import IngestOutcome

HEADERS = {"X-API-Key": settings.api_key}


@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setattr(limiter, "enabled", False)
    app = FastAPI()
    app.state.limiter = limiter
    app.include_router(pipeline_routes.router)
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


def add_post(db, review_status, **fields):
    post = SalaryPost(raw_text="test post", review_status=review_status, **fields)
    db.add(post)
    db.flush()
    return post


def stub_pipeline(monkeypatch, outcome):
    async def fake(db, raw_text, source="manual", **kwargs):
        return outcome

    monkeypatch.setattr(pipeline_routes, "ingest_pipeline", fake)


@pytest.mark.parametrize(
    "outcome, expected_code",
    [
        (IngestOutcome(status="approved", post_id=1), 201),
        (IngestOutcome(status="pending", post_id=2), 202),
        (IngestOutcome(status="duplicate", duplicate_of=3), 409),
        (IngestOutcome(status="rejected"), 422),
    ],
)
def test_post_status_codes(client, monkeypatch, outcome, expected_code):
    stub_pipeline(monkeypatch, outcome)

    response = client.post("/posts", json={"raw_text": "hello"}, headers=HEADERS)

    assert response.status_code == expected_code
    assert response.json()["status"] == outcome.status


def test_post_requires_api_key(client):
    response = client.post("/posts", json={"raw_text": "hello"})

    assert response.status_code == 401


def test_post_rejects_empty_and_oversized_text(client):
    assert client.post("/posts", json={"raw_text": ""}, headers=HEADERS).status_code == 422
    too_long = {"raw_text": "x" * 5001}
    assert client.post("/posts", json=too_long, headers=HEADERS).status_code == 422


def test_pending_list_contains_only_pending(client, db):
    pending = add_post(db, "pending", role="devops")
    approved = add_post(db, "approved", role="backend")

    ids = [item["id"] for item in client.get("/review/pending", headers=HEADERS).json()]

    assert pending.id in ids
    assert approved.id not in ids


def test_approve_pending_post(client, db):
    post = add_post(db, "pending")

    response = client.post(f"/review/{post.id}/approve", headers=HEADERS)

    assert response.status_code == 200
    assert response.json()["review_status"] == "approved"


def test_approve_is_idempotent(client, db):
    post = add_post(db, "approved")

    response = client.post(f"/review/{post.id}/approve", headers=HEADERS)

    assert response.status_code == 200


def test_reject_marks_post_as_rejected_without_deleting(client, db):
    post = add_post(db, "pending")

    response = client.post(f"/review/{post.id}/reject", headers=HEADERS)

    assert response.json()["review_status"] == "rejected"
    assert db.get(SalaryPost, post.id) is not None


def test_cannot_approve_a_rejected_post(client, db):
    post = add_post(db, "rejected")

    response = client.post(f"/review/{post.id}/approve", headers=HEADERS)

    assert response.status_code == 409


def test_unknown_post_returns_404(client):
    response = client.post("/review/999999999/approve", headers=HEADERS)

    assert response.status_code == 404
