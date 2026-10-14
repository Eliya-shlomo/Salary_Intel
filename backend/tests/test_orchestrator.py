import asyncio
import uuid

import pytest

from app.agents.critic_agent import CriticVerdict
from app.agents.extractor_agent import PostExtraction
from app.db.models import SalaryPost
from app.ingestion.orchestrator import ingest_pipeline

DIMENSIONS = 1536


def unit_vector(*leading):
    return list(leading) + [0.0] * (DIMENSIONS - len(leading))


def new_post_text():
    return f"{uuid.uuid4()} מהנדס Devops בסטארטאפ. 62 א׳ ברוטו + אופציות"


class Spy:
    def __init__(self, extraction=None, agrees=True, vector=None):
        self.extraction = extraction
        self.agrees = agrees
        self.vector = vector or unit_vector(0.0, 0.0, 1.0)
        self.extract_calls = 0
        self.critique_calls = 0
        self.embed_calls = 0

    async def extract(self, raw_text, feedback):
        self.extract_calls += 1
        return self.extraction

    async def critique(self, raw_text, candidate):
        self.critique_calls += 1
        return CriticVerdict(agrees=self.agrees, issues=[] if self.agrees else ["x"])

    async def embed(self, text):
        self.embed_calls += 1
        return self.vector


def salary_extraction(**overrides):
    fields = {
        "is_salary_post": True,
        "role_text": "מהנדס Devops",
        "salary_text": "62 א׳ ברוטו",
        "years_experience": None,
        "has_equity": True,
        "evidence": "62 א׳ ברוטו + אופציות",
    }
    fields.update(overrides)
    return PostExtraction(**fields)


def run(db, text, spy):
    return asyncio.run(
        ingest_pipeline(
            db, text, extract=spy.extract, critique=spy.critique, embed=spy.embed
        )
    )


def stored(db, text):
    return db.query(SalaryPost).filter(SalaryPost.raw_text == text).all()


def test_good_post_is_saved_as_approved(db):
    text = new_post_text()
    spy = Spy(salary_extraction())

    outcome = run(db, text, spy)

    assert outcome.status == "approved"
    rows = stored(db, text)
    assert len(rows) == 1
    assert rows[0].review_status == "approved"
    assert rows[0].salary_min == 62_000
    assert rows[0].embedding is not None


def test_critic_disagreement_goes_to_pending(db):
    text = new_post_text()
    spy = Spy(salary_extraction(), agrees=False)

    outcome = run(db, text, spy)

    assert outcome.status == "pending"
    assert stored(db, text)[0].review_status == "pending"
    assert spy.extract_calls == 2


def test_noise_post_is_rejected_and_not_saved(db):
    text = new_post_text()
    spy = Spy(salary_extraction(is_salary_post=False, salary_text=None, evidence=None))

    outcome = run(db, text, spy)

    assert outcome.status == "rejected"
    assert stored(db, text) == []


def test_exact_duplicate_stops_before_any_model_call(db):
    text = new_post_text()
    existing = SalaryPost(raw_text=text)
    db.add(existing)
    db.flush()
    spy = Spy(salary_extraction())

    outcome = run(db, text, spy)

    assert outcome.status == "duplicate"
    assert outcome.duplicate_of == existing.id
    assert spy.embed_calls == 0
    assert spy.extract_calls == 0


def test_near_duplicate_stops_before_extraction(db):
    existing = SalaryPost(raw_text=new_post_text(), embedding=unit_vector(1.0))
    db.add(existing)
    db.flush()
    spy = Spy(salary_extraction(), vector=unit_vector(1.0, 0.01))

    outcome = run(db, new_post_text() + " 🙂", spy)

    assert outcome.status == "duplicate"
    assert outcome.duplicate_of == existing.id
    assert spy.embed_calls == 1
    assert spy.extract_calls == 0


def test_empty_text_is_an_error(db):
    with pytest.raises(ValueError):
        run(db, "   ", Spy(salary_extraction()))
