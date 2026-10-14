from sqlalchemy.orm import Session

from app.db.models import SalaryPost
from app.ingestion.review_loop import ReviewResult

REVIEW_STATUS_BY_RESULT = {"approved": "approved", "needs_review": "pending"}


def save_review_result(
    db: Session,
    raw_text: str,
    result: ReviewResult,
    source: str = "manual",
    embedding: list[float] | None = None,
) -> SalaryPost | None:
    review_status = REVIEW_STATUS_BY_RESULT.get(result.status)
    if review_status is None or result.candidate is None:
        return None

    candidate = result.candidate
    post = SalaryPost(
        raw_text=raw_text,
        role=candidate.role,
        role_canonical=candidate.role,
        years_experience=candidate.years_experience,
        salary_min=candidate.salary_min,
        salary_max=candidate.salary_max,
        pay_basis=candidate.pay_basis,
        has_equity=candidate.has_equity,
        evidence=candidate.evidence,
        source=source,
        embedding=embedding,
        review_status=review_status,
    )
    db.add(post)
    db.flush()
    return post
