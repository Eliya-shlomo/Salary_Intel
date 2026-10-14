from app.db.models import SalaryPost
from app.tools.compute_stats import compute_stats

TEST_YEARS = 99.0


def add_post(db, salary_min, salary_max=None, **overrides):
    fields = {
        "raw_text": "test post",
        "role": "Backend Developer",
        "role_canonical": "backend",
        "years_experience": TEST_YEARS,
        "salary_min": salary_min,
        "salary_max": salary_max if salary_max is not None else salary_min,
        "pay_basis": "gross",
        "review_status": "approved",
    }
    fields.update(overrides)
    db.add(SalaryPost(**fields))
    db.flush()


def test_percentiles_with_outlier(db):
    for amount in [20_000, 22_000, 25_000, 30_000, 200_000]:
        add_post(db, amount)

    stats = compute_stats(db, min_years=TEST_YEARS)

    assert stats.n == 5
    assert stats.p25 == 22_000
    assert stats.p50 == 25_000
    assert stats.p75 == 30_000


def test_too_few_posts_returns_no_percentiles(db):
    for amount in [20_000, 25_000, 30_000]:
        add_post(db, amount)

    stats = compute_stats(db, min_years=TEST_YEARS)

    assert stats.n == 3
    assert stats.p50 is None
    assert "need at least 5" in stats.note


def test_range_uses_midpoint(db):
    for _ in range(5):
        add_post(db, 50_000, 60_000)

    stats = compute_stats(db, min_years=TEST_YEARS)

    assert stats.p50 == 55_000


def test_pending_posts_are_excluded(db):
    for amount in [20_000, 22_000, 25_000, 30_000]:
        add_post(db, amount)
    add_post(db, 200_000, review_status="pending")

    stats = compute_stats(db, min_years=TEST_YEARS)

    assert stats.n == 4


def test_role_filter_uses_canonical_role(db):
    for amount in [20_000, 22_000, 25_000, 30_000, 35_000]:
        add_post(db, amount, role="DevOps Engineer", role_canonical="devops")
    add_post(db, 90_000, role="Frontend Developer", role_canonical="frontend")

    stats = compute_stats(db, role="devops", min_years=TEST_YEARS)

    assert stats.n == 5
    assert stats.p50 == 25_000


def test_pay_basis_filter(db):
    for amount in [20_000, 22_000, 25_000, 30_000, 35_000]:
        add_post(db, amount, pay_basis="net")
    add_post(db, 90_000, pay_basis="gross")

    stats = compute_stats(db, pay_basis="net", min_years=TEST_YEARS)

    assert stats.n == 5
