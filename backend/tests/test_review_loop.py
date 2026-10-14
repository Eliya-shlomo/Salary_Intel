import asyncio

from app.agents.critic_agent import CriticVerdict
from app.agents.extractor_agent import PostExtraction
from app.ingestion.review_loop import extract_with_review

POST = "מהנדס Devops בסטארטאפ. 62 א׳ ברוטו + אופציות. יומיים מהבית"


def good_extraction(**overrides):
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


class FakeAgents:
    def __init__(self, extractions, verdicts):
        self.extractions = list(extractions)
        self.verdicts = list(verdicts)
        self.extract_calls = 0
        self.critique_calls = 0
        self.feedback_seen = []

    async def extract(self, raw_text, feedback):
        self.extract_calls += 1
        self.feedback_seen.append(list(feedback))
        return self.extractions.pop(0)

    async def critique(self, raw_text, candidate):
        self.critique_calls += 1
        return self.verdicts.pop(0)


def run(agents):
    return asyncio.run(
        extract_with_review(POST, extract=agents.extract, critique=agents.critique)
    )


def test_approved_in_first_round():
    agents = FakeAgents([good_extraction()], [CriticVerdict(agrees=True, issues=[])])

    result = run(agents)

    assert result.status == "approved"
    assert result.rounds == 1
    assert result.candidate.salary_min == 62_000


def test_critic_feedback_reaches_extractor_on_retry():
    agents = FakeAgents(
        [good_extraction(), good_extraction()],
        [
            CriticVerdict(agrees=False, issues=["Second offer is missing."]),
            CriticVerdict(agrees=True, issues=[]),
        ],
    )

    result = run(agents)

    assert result.status == "approved"
    assert result.rounds == 2
    assert agents.feedback_seen == [[], ["Second offer is missing."]]


def test_no_agreement_after_two_rounds_goes_to_review():
    agents = FakeAgents(
        [good_extraction(), good_extraction()],
        [
            CriticVerdict(agrees=False, issues=["Wrong basis."]),
            CriticVerdict(agrees=False, issues=["Still wrong basis."]),
        ],
    )

    result = run(agents)

    assert result.status == "needs_review"
    assert result.rounds == 2
    assert result.issues == ["Still wrong basis."]


def test_missing_evidence_skips_the_critic():
    bad = good_extraction(evidence="משכורת 90 א׳ נטו")
    agents = FakeAgents([bad, bad], [])

    result = run(agents)

    assert result.status == "needs_review"
    assert agents.critique_calls == 0
    assert agents.extract_calls == 2


def test_noise_post_is_rejected_without_calling_the_critic():
    noise = good_extraction(is_salary_post=False, salary_text=None, evidence=None)
    agents = FakeAgents([noise], [])

    result = run(agents)

    assert result.status == "rejected"
    assert agents.critique_calls == 0
    assert result.rounds == 1
