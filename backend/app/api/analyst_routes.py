from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.agents.analyst_agent import run_analyst
from app.agents.verifier import verify_answer
from app.core.logging import get_logger
from app.core.rate_limiter import limiter
from app.core.security import verify_api_key
from app.db.database import get_db
from app.tools.compare_offers import OfferComparison, compare_offer
from app.tools.compute_stats import PayBasis
from app.tools.normalize_role import CanonicalRole

logger = get_logger(__name__)
router = APIRouter()

UNVERIFIED_MESSAGE = "The answer contained numbers that could not be verified against the data."


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=500)


class AskResponse(BaseModel):
    answer: str | None
    verified: bool
    unsupported: list[float]
    message: str | None = None


@router.post("/analyst/ask", response_model=AskResponse)
@limiter.limit("10/minute")
async def ask_analyst(
    request: Request,
    body: AskRequest,
    api_key: str = Depends(verify_api_key),
):
    try:
        run = await run_analyst(body.question)
    except Exception as e:
        logger.error(f"Analyst error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error answering question")

    verification = verify_answer(body.question, run.answer, run.reports)
    if not verification.ok:
        logger.warning(f"Unverified analyst answer, numbers: {verification.unsupported}")
        return AskResponse(
            answer=None,
            verified=False,
            unsupported=verification.unsupported,
            message=UNVERIFIED_MESSAGE,
        )
    return AskResponse(answer=run.answer, verified=True, unsupported=[])


class OfferRequest(BaseModel):
    salary: float = Field(gt=0, le=1_000_000)
    role: CanonicalRole | None = None
    pay_basis: PayBasis | None = None
    min_years: float | None = Field(default=None, ge=0, le=50)
    max_years: float | None = Field(default=None, ge=0, le=50)


class CompareRequest(BaseModel):
    offers: list[OfferRequest] = Field(min_length=2, max_length=2)


class CompareResponse(BaseModel):
    comparisons: list[OfferComparison]
    better_vs_market: int | None


@router.post("/analyst/compare", response_model=CompareResponse)
@limiter.limit("30/minute")
def compare_offers_endpoint(
    request: Request,
    body: CompareRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    comparisons = [
        compare_offer(
            db,
            salary=offer.salary,
            role=offer.role,
            pay_basis=offer.pay_basis,
            min_years=offer.min_years,
            max_years=offer.max_years,
        )
        for offer in body.offers
    ]
    first, second = (c.vs_median_pct for c in comparisons)
    better = None
    if first is not None and second is not None and first != second:
        better = 0 if first > second else 1
    return CompareResponse(comparisons=comparisons, better_vs_market=better)
