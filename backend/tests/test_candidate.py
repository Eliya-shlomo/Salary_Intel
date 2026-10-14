from app.agents.extractor_agent import PostExtraction
from app.ingestion.candidate import build_candidate

POST = "מהנדס Devops בסטארטאפ. 62 א׳ ברוטו + אופציות. יומיים מהבית. עשור ניסיון"


def make_extraction(**overrides):
    fields = {
        "is_salary_post": True,
        "role_text": "מהנדס Devops",
        "salary_text": "62 א׳ ברוטו",
        "years_experience": 10,
        "has_equity": True,
        "evidence": "62 א׳ ברוטו + אופציות",
    }
    fields.update(overrides)
    return PostExtraction(**fields)


def test_numbers_come_from_tools_not_from_model():
    candidate = build_candidate(POST, make_extraction())

    assert candidate.role == "devops"
    assert candidate.salary_min == 62_000
    assert candidate.salary_max == 62_000
    assert candidate.pay_basis == "gross"
    assert candidate.evidence_found is True


def test_invented_evidence_is_flagged():
    candidate = build_candidate(POST, make_extraction(evidence="משכורת 90 א׳ נטו"))

    assert candidate.evidence_found is False


def test_missing_evidence_is_flagged():
    candidate = build_candidate(POST, make_extraction(evidence=None))

    assert candidate.evidence_found is False


def test_evidence_ignores_whitespace_differences():
    candidate = build_candidate(POST, make_extraction(evidence="62 א׳   ברוטו"))

    assert candidate.evidence_found is True


def test_post_without_salary_text_has_no_amount():
    candidate = build_candidate(
        "מה לעשות מפה?",
        make_extraction(is_salary_post=False, salary_text=None, evidence=None),
    )

    assert candidate.salary_min is None
    assert candidate.pay_basis == "unknown"
