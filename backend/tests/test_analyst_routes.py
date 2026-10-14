import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.agents.analyst_agent import AnalystRun
from app.api import analyst_routes
from app.core.config import settings
from app.core.rate_limiter import limiter
from app.db.database import get_db
from app.db.models import SalaryPost

HEADERS = {"X-API-Key": settings.api_key}
REPORT = 'Median 43,500.\n\nTOOL_DATA:\n["{\\"n\\": 66, \\"p50\\": 43500.0}"]'


@pytest.fixture
def client(db, monkeypatch):
    monkeypatch.setattr(limiter, "enabled", False)
    app = FastAPI()
    app.state.limiter = limiter
    app.include_router(analyst_routes.router)
    app.dependency_overrides[get_db] = lambda: db
    return TestClient(app)


def stub_analyst(monkeypatch, answer):
    async def fake(question):
        return AnalystRun(answer=answer, reports=[REPORT])

    monkeypatch.setattr(analyst_routes, "run_analyst", fake)


def test_verified_answer_is_returned(client, monkeypatch):
    stub_analyst(monkeypatch, "The median is 43,500 NIS from 66 posts.")

    response = client.post("/analyst/ask", json={"question": "devops?"}, headers=HEADERS)

    assert response.status_code == 200
    assert response.json() == {
        "answer": "The median is 43,500 NIS from 66 posts.",
        "verified": True,
        "unsupported": [],
        "message": None,
    }


def test_answer_with_invented_number_is_withheld(client, monkeypatch):
    stub_analyst(monkeypatch, "The median is 52,000 NIS.")

    response = client.post("/analyst/ask", json={"question": "devops?"}, headers=HEADERS)

    body = response.json()
    assert response.status_code == 200
    assert body["answer"] is None
    assert body["verified"] is False
    assert body["unsupported"] == [52000.0]


def test_agent_failure_returns_500_without_details(client, monkeypatch):
    async def boom(question):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr(analyst_routes, "run_analyst", boom)

    response = client.post("/analyst/ask", json={"question": "devops?"}, headers=HEADERS)

    assert response.status_code == 500
    assert "secret" not in response.text


def test_empty_question_is_rejected(client):
    response = client.post("/analyst/ask", json={"question": ""}, headers=HEADERS)

    assert response.status_code == 422


def test_missing_api_key_is_rejected(client):
    response = client.post("/analyst/ask", json={"question": "devops?"})

    assert response.status_code in (401, 403)


TEST_YEARS = 49.0


def add_market(db, amounts):
    for amount in amounts:
        db.add(
            SalaryPost(
                raw_text="test post",
                role="Backend Developer",
                role_canonical="backend",
                years_experience=TEST_YEARS,
                salary_min=amount,
                salary_max=amount,
                pay_basis="gross",
                review_status="approved",
            )
        )
    db.flush()


def offer(salary, **fields):
    return {"salary": salary, "min_years": TEST_YEARS, **fields}


def test_compare_picks_offer_further_above_market(client, db):
    add_market(db, [20_000, 22_000, 25_000, 28_000, 30_000])

    response = client.post(
        "/analyst/compare",
        json={"offers": [offer(26_000), offer(30_000)]},
        headers=HEADERS,
    )

    body = response.json()
    assert response.status_code == 200
    assert [c["vs_median_pct"] for c in body["comparisons"]] == [4.0, 20.0]
    assert body["better_vs_market"] == 1


def test_compare_without_enough_data_has_no_winner(client, db):
    add_market(db, [20_000, 25_000])

    response = client.post(
        "/analyst/compare",
        json={"offers": [offer(26_000), offer(30_000)]},
        headers=HEADERS,
    )

    body = response.json()
    assert body["better_vs_market"] is None
    assert body["comparisons"][0]["position"] == "unknown"


@pytest.mark.parametrize(
    "offers",
    [[], [{"salary": 30_000}], [{"salary": 0}, {"salary": 1}], [{"salary": 1, "role": "gardener"}] * 2],
)
def test_compare_rejects_invalid_requests(client, offers):
    response = client.post("/analyst/compare", json={"offers": offers}, headers=HEADERS)

    assert response.status_code == 422
