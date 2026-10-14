import pytest

from app.db.models import SalaryPost
from app.tools.compare_offers import compare_offer, position_in_range
from app.tools.compute_stats import SalaryStats

TEST_YEARS = 99.0
STATS = SalaryStats(n=10, p25=20_000, p50=25_000, p75=30_000, note="ok")
NO_STATS = SalaryStats(n=2, p25=None, p50=None, p75=None, note="too few")


@pytest.mark.parametrize(
    "salary, expected",
    [
        (19_999, "below_p25"),
        (20_000, "p25_to_p50"),
        (24_999, "p25_to_p50"),
        (25_000, "p50_to_p75"),
        (30_000, "above_p75"),
        (80_000, "above_p75"),
    ],
)
def test_position_boundaries(salary, expected):
    assert position_in_range(salary, STATS) == expected


def test_position_is_unknown_without_percentiles():
    assert position_in_range(25_000, NO_STATS) == "unknown"


def add_posts(db, amounts):
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


def test_compare_offer_against_real_stats(db):
    add_posts(db, [20_000, 22_000, 25_000, 28_000, 30_000])

    result = compare_offer(db, salary=30_000, min_years=TEST_YEARS)

    assert result.n == 5
    assert result.position == "above_p75"
    assert result.vs_median_pct == 20.0


def test_compare_offer_with_too_few_posts_has_no_percent(db):
    add_posts(db, [20_000, 25_000])

    result = compare_offer(db, salary=30_000, min_years=TEST_YEARS)

    assert result.position == "unknown"
    assert result.vs_median_pct is None
    assert "need at least 5" in result.note
