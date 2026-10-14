from typing import Awaitable, Callable, Literal

from pydantic import BaseModel

from app.agents.critic_agent import CriticVerdict, critique_candidate
from app.agents.extractor_agent import PostExtraction, extract_post
from app.ingestion.candidate import Candidate, build_candidate

MAX_ROUNDS = 2

ExtractFn = Callable[[str, list[str]], Awaitable[PostExtraction]]
CritiqueFn = Callable[[str, Candidate], Awaitable[CriticVerdict]]


class ReviewResult(BaseModel):
    status: Literal["approved", "needs_review", "rejected"]
    candidate: Candidate | None
    issues: list[str]
    rounds: int


async def extract_with_review(
    raw_text: str,
    extract: ExtractFn = extract_post,
    critique: CritiqueFn = critique_candidate,
) -> ReviewResult:
    issues: list[str] = []
    candidate: Candidate | None = None

    for round_number in range(1, MAX_ROUNDS + 1):
        extraction = await extract(raw_text, issues)
        candidate = build_candidate(raw_text, extraction)

        if not candidate.is_salary_post:
            return ReviewResult(
                status="rejected", candidate=candidate, issues=[], rounds=round_number
            )

        if not candidate.evidence_found:
            issues = ["The evidence quote does not appear in the post."]
            continue

        verdict = await critique(raw_text, candidate)
        if verdict.agrees:
            return ReviewResult(
                status="approved", candidate=candidate, issues=[], rounds=round_number
            )
        issues = verdict.issues

    return ReviewResult(
        status="needs_review", candidate=candidate, issues=issues, rounds=MAX_ROUNDS
    )
