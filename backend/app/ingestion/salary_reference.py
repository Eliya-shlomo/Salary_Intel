"""The salary reference table that calibrates the synthetic posts.

salary_reference.json holds salary ranges exactly as each source published
them (observations), and the weights used for everything else. Cells
(p25 / median / p75 per role and bucket) are derived here by a fixed rule,
so every number in the dataset can be traced back to the rows it came from.

    python -m app.ingestion.salary_reference      prints the derived table
"""
import json
from pathlib import Path
from statistics import mean, median
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.tools.normalize_role import CanonicalRole

REFERENCE_PATH = Path(__file__).parent / "salary_reference.json"

Confidence = Literal["high", "medium", "low"]
Style = Literal["update", "offer_question", "compare_offers", "question_no_salary"]
StatedBasis = Literal["gross", "unknown"]

ROUND_CELL_TO = 100


class Source(BaseModel):
    id: str
    publisher: str
    url: str
    year: int
    accessed: str
    notes: str = ""


class Bucket(BaseModel):
    name: str
    min_years: int
    max_years: int

    @model_validator(mode="after")
    def check_range(self):
        if self.min_years > self.max_years:
            raise ValueError(f"bucket {self.name}: min_years > max_years")
        return self


class Observation(BaseModel):
    """One published range, copied as the source printed it."""

    source: str
    source_role: str
    role: CanonicalRole
    source_bucket: str
    bucket: str
    low: int = Field(gt=0)
    high: int = Field(gt=0)
    mapping_uncertain: bool = False
    note: str = ""

    @model_validator(mode="after")
    def check_order(self):
        if self.low > self.high:
            raise ValueError(f"{self.source} {self.source_role}: low > high")
        return self


class Cell(BaseModel):
    role: CanonicalRole
    bucket: str
    p25: int
    median: int
    p75: int
    sources: list[str]
    publishers: int
    confidence: Confidence
    year: int


class Weights(BaseModel):
    """A distribution over keys, with where it came from."""

    values: dict[str, float]
    sources: list[str] = []
    assumption: bool = False
    notes: str = ""

    @model_validator(mode="after")
    def check_values(self):
        if not self.values or any(v < 0 for v in self.values.values()):
            raise ValueError("weights must be non-empty and non-negative")
        if not self.sources and not self.assumption:
            raise ValueError("weights need a source or must be marked as an assumption")
        return self


class Probability(BaseModel):
    value: float = Field(ge=0, le=1)
    sources: list[str] = []
    assumption: bool = False
    notes: str = ""

    @model_validator(mode="after")
    def check_origin(self):
        if not self.sources and not self.assumption:
            raise ValueError("a probability needs a source or must be marked as an assumption")
        return self


def _round(value: float) -> int:
    return int(round(value / ROUND_CELL_TO) * ROUND_CELL_TO)


def confidence_for(
    publishers: int, midpoints: list[float], mapping_uncertain: bool = False
) -> Confidence:
    """high: 3+ publishers within 15% of each other; medium: 2+ within 25%.

    A cell built on a row whose role or bucket mapping is uncertain is low.
    """
    if mapping_uncertain:
        return "low"
    spread = (max(midpoints) - min(midpoints)) / median(midpoints)
    if publishers >= 3 and spread <= 0.15:
        return "high"
    if publishers >= 2 and spread <= 0.25:
        return "medium"
    return "low"


def derive_cell(
    role: str, bucket: str, observations: list[Observation], sources: dict[str, Source]
) -> Cell:
    """Collapse each publisher to one range, then take medians across publishers.

    A published from-to range is read as that publisher's p25-p75, so
    p25 = median of lows, p75 = median of highs, median = median of midpoints.
    """
    by_publisher: dict[str, list[Observation]] = {}
    for obs in observations:
        by_publisher.setdefault(sources[obs.source].publisher, []).append(obs)

    lows, highs = [], []
    for rows in by_publisher.values():
        lows.append(mean(o.low for o in rows))
        highs.append(mean(o.high for o in rows))
    midpoints = [(lo + hi) / 2 for lo, hi in zip(lows, highs)]

    source_ids = sorted({o.source for o in observations})
    return Cell(
        role=role,
        bucket=bucket,
        p25=_round(median(lows)),
        median=_round(median(midpoints)),
        p75=_round(median(highs)),
        sources=source_ids,
        publishers=len(by_publisher),
        confidence=confidence_for(
            len(by_publisher), midpoints, any(o.mapping_uncertain for o in observations)
        ),
        year=max(sources[s].year for s in source_ids),
    )


class SalaryReference(BaseModel):
    version: str
    method: dict[str, str]
    sources: list[Source] = Field(min_length=1)
    buckets: list[Bucket] = Field(min_length=1)
    observations: list[Observation] = Field(min_length=1)
    role_weights: Weights
    bucket_weights: Weights
    style_weights: Weights
    basis_weights: Weights
    city_weights: Weights
    equity_share: Probability
    cells: list[Cell] = []

    @model_validator(mode="after")
    def check_and_derive(self):
        sources = {s.id: s for s in self.sources}
        bucket_names = {b.name for b in self.buckets}

        used = [o.source for o in self.observations]
        for item in self._all_weights():
            used += item.sources
        unknown = set(used) - set(sources)
        if unknown:
            raise ValueError(f"unknown source ids: {sorted(unknown)}")
        for obs in self.observations:
            if obs.bucket not in bucket_names:
                raise ValueError(f"unknown bucket: {obs.bucket}")

        grouped: dict[tuple[str, str], list[Observation]] = {}
        for obs in self.observations:
            grouped.setdefault((obs.role, obs.bucket), []).append(obs)
        self.cells = [
            derive_cell(role, bucket, rows, sources)
            for (role, bucket), rows in grouped.items()
        ]

        cell_roles = {cell.role for cell in self.cells}
        if set(self.role_weights.values) - cell_roles:
            raise ValueError("role_weights names a role that has no cells")
        if set(self.bucket_weights.values) - bucket_names:
            raise ValueError("bucket_weights names an unknown bucket")
        if set(self.style_weights.values) - set(Style.__args__):
            raise ValueError("style_weights names an unknown style")
        if set(self.basis_weights.values) - set(StatedBasis.__args__):
            raise ValueError("basis_weights names an unsupported basis")
        return self

    def _all_weights(self) -> list:
        return [
            self.role_weights,
            self.bucket_weights,
            self.style_weights,
            self.basis_weights,
            self.city_weights,
            self.equity_share,
        ]

    def cell(self, role: str, bucket: str) -> Cell | None:
        for cell in self.cells:
            if cell.role == role and cell.bucket == bucket:
                return cell
        return None

    def bucket(self, name: str) -> Bucket:
        return next(b for b in self.buckets if b.name == name)


def load_reference(path: Path = REFERENCE_PATH) -> SalaryReference:
    return SalaryReference.model_validate(json.loads(path.read_text(encoding="utf-8")))


def main() -> None:
    reference = load_reference()
    order = {b.name: i for i, b in enumerate(reference.buckets)}
    print(f"{'role':16} {'bucket':7} {'p25':>7} {'median':>7} {'p75':>7}  pubs  conf    sources")
    for c in sorted(reference.cells, key=lambda c: (c.role, order[c.bucket])):
        print(
            f"{c.role:16} {c.bucket:7} {c.p25:>7,} {c.median:>7,} {c.p75:>7,}"
            f"  {c.publishers:>4}  {c.confidence:6}  {', '.join(c.sources)}"
        )


if __name__ == "__main__":
    main()
