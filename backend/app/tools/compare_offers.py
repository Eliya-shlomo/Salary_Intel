from typing import Literal

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.tools.compute_stats import PayBasis, SalaryStats, compute_stats
from app.tools.normalize_role import CanonicalRole

Position = Literal["below_p25", "p25_to_p50", "p50_to_p75", "above_p75", "unknown"]


class OfferComparison(BaseModel):
    salary: float
    n: int
    position: Position
    vs_median_pct: float | None
    note: str


def position_in_range(salary: float, stats: SalaryStats) -> Position:
    if stats.p25 is None or stats.p50 is None or stats.p75 is None:
        return "unknown"
    if salary < stats.p25:
        return "below_p25"
    if salary < stats.p50:
        return "p25_to_p50"
    if salary < stats.p75:
        return "p50_to_p75"
    return "above_p75"


def compare_offer(
    db: Session,
    salary: float,
    role: CanonicalRole | None = None,
    pay_basis: PayBasis | None = None,
    min_years: float | None = None,
    max_years: float | None = None,
) -> OfferComparison:
    stats = compute_stats(
        db, role=role, pay_basis=pay_basis, min_years=min_years, max_years=max_years
    )
    position = position_in_range(salary, stats)
    vs_median = None
    if stats.p50:
        vs_median = round((salary - stats.p50) / stats.p50 * 100, 1)
    return OfferComparison(
        salary=salary,
        n=stats.n,
        position=position,
        vs_median_pct=vs_median,
        note=stats.note,
    )
