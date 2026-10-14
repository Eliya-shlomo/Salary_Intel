import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import routes
from app.core.config import settings
from app.core.rate_limiter import limiter

HEADERS = {"X-API-Key": settings.api_key}


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(limiter, "enabled", False)
    app = FastAPI()
    app.state.limiter = limiter
    app.include_router(routes.router)
    return TestClient(app)


def test_query_returns_only_a_snippet_of_each_source(client, monkeypatch):
    async def fake(query):
        return {
            "answer": "ok",
            "posts_used": 1,
            "sources": [{"id": 1, "raw_text": "x" * 1000, "role": "devops"}],
        }

    monkeypatch.setattr(routes, "answer_salary_query", fake)

    response = client.post("/query", json={"query": "devops?"}, headers=HEADERS)

    source = response.json()["sources"][0]
    assert len(source["raw_text"]) == routes.SNIPPET_CHARS
    assert source["role"] == "devops"


def test_cors_origins_are_split_from_one_setting(monkeypatch):
    monkeypatch.setattr(settings, "allowed_origins", "https://a.com, https://b.com")

    assert settings.cors_origins == ["https://a.com", "https://b.com"]
