from app.ingestion.candidate import Candidate
from app.ingestion.persist import save_review_result
from app.ingestion.review_loop import ReviewResult


def make_result(status):
    candidate = Candidate(
        is_salary_post=status != "rejected",
        role="devops",
        salary_min=62_000,
        salary_max=62_000,
        pay_basis="gross",
        years_experience=10,
        has_equity=True,
        evidence="62 א׳ ברוטו",
        evidence_found=True,
    )
    return ReviewResult(status=status, candidate=candidate, issues=[], rounds=1)


def test_approved_result_is_saved_as_approved(db):
    post = save_review_result(db, "62 א׳ ברוטו", make_result("approved"))

    assert post.id is not None
    assert post.review_status == "approved"
    assert post.role == "devops"
    assert post.role_canonical == "devops"
    assert post.salary_min == 62_000


def test_needs_review_result_waits_in_the_queue(db):
    post = save_review_result(db, "62 א׳ ברוטו", make_result("needs_review"))

    assert post.review_status == "pending"


def test_rejected_result_is_not_saved(db):
    assert save_review_result(db, "מה לעשות מפה?", make_result("rejected")) is None
