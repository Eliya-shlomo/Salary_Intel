from pydantic import BaseModel

from app.agents.extractor_agent import PostExtraction
from app.tools.normalize_role import CanonicalRole, normalize_role
from app.tools.parse_amount import PayBasisValue, parse_amount


class Candidate(BaseModel):
    is_salary_post: bool
    role: CanonicalRole
    salary_min: float | None
    salary_max: float | None
    pay_basis: PayBasisValue
    years_experience: float | None
    has_equity: bool | None
    evidence: str | None
    evidence_found: bool


def _squash(text: str) -> str:
    return " ".join(text.split())


def build_candidate(raw_text: str, extraction: PostExtraction) -> Candidate:
    amount = parse_amount(extraction.salary_text or "")
    evidence_found = bool(
        extraction.evidence and _squash(extraction.evidence) in _squash(raw_text)
    )

    return Candidate(
        is_salary_post=extraction.is_salary_post,
        role=normalize_role(extraction.role_text or ""),
        salary_min=amount.salary_min,
        salary_max=amount.salary_max,
        pay_basis=amount.pay_basis,
        years_experience=extraction.years_experience,
        has_equity=extraction.has_equity,
        evidence=extraction.evidence,
        evidence_found=evidence_found,
    )
