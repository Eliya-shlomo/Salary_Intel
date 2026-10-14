from typing import Literal

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.tools.normalize_role import CanonicalRole

MIN_SAMPLE = 5

PayBasis = Literal["gross", "net", "unknown"]

STATS_SQL = text(
    """
    SELECT
        count(*) AS n,
        percentile_cont(0.25) WITHIN GROUP (ORDER BY amount) AS p25,
        percentile_cont(0.50) WITHIN GROUP (ORDER BY amount) AS p50,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY amount) AS p75
    FROM (
        SELECT COALESCE((salary_min + salary_max) / 2, salary) AS amount
        FROM salary_posts
        WHERE review_status = 'approved'
          AND (:role IS NULL OR role_canonical = :role)
          AND (:pay_basis IS NULL OR pay_basis = :pay_basis)
          AND (:min_years IS NULL OR years_experience >= :min_years)
          AND (:max_years IS NULL OR years_experience <= :max_years)
    ) AS filtered
    WHERE amount IS NOT NULL
    """
)


class SalaryStats(BaseModel):
    n: int
    p25: float | None
    p50: float | None
    p75: float | None
    note: str


def compute_stats(
    db: Session,
    role: CanonicalRole | None = None,
    pay_basis: PayBasis | None = None,
    min_years: float | None = None,
    max_years: float | None = None,
) -> SalaryStats:
    row = db.execute(
        STATS_SQL,
        {
            "role": role,
            "pay_basis": pay_basis,
            "min_years": min_years,
            "max_years": max_years,
        },
    ).one()

    if row.n < MIN_SAMPLE:
        return SalaryStats(
            n=row.n,
            p25=None,
            p50=None,
            p75=None,
            note=(
                f"Only {row.n} matching posts, need at least {MIN_SAMPLE}. "
                "Try removing a filter such as years of experience or pay_basis."
            ),
        )

    return SalaryStats(
        n=row.n,
        p25=round(row.p25),
        p50=round(row.p50),
        p75=round(row.p75),
        note="Percentiles of monthly salary in NIS over approved posts.",
    )
