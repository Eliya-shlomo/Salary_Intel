from typing import Awaitable, Callable, Literal

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.critic_agent import critique_candidate
from app.agents.extractor_agent import extract_post
from app.ingestion.persist import save_review_result
from app.ingestion.review_loop import CritiqueFn, ExtractFn, extract_with_review
from app.rag.embeddings import get_embedding
from app.tools.find_duplicate import find_duplicate

EmbedFn = Callable[[str], Awaitable[list[float]]]

OUTCOME_BY_REVIEW_STATUS = {
    "approved": "approved",
    "needs_review": "pending",
    "rejected": "rejected",
}


class IngestOutcome(BaseModel):
    status: Literal["approved", "pending", "rejected", "duplicate"]
    post_id: int | None = None
    duplicate_of: int | None = None
    issues: list[str] = []


async def ingest_pipeline(
    db: Session,
    raw_text: str,
    source: str = "manual",
    extract: ExtractFn = extract_post,
    critique: CritiqueFn = critique_candidate,
    embed: EmbedFn = get_embedding,
) -> IngestOutcome:
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty text — cannot ingest")

    exact = find_duplicate(db, raw_text)
    if exact:
        return IngestOutcome(status="duplicate", duplicate_of=exact.post_id)

    embedding = await embed(raw_text)
    near = find_duplicate(db, raw_text, embedding=embedding)
    if near:
        return IngestOutcome(status="duplicate", duplicate_of=near.post_id)

    result = await extract_with_review(raw_text, extract=extract, critique=critique)
    post = save_review_result(
        db, raw_text, result, source=source, embedding=embedding
    )

    return IngestOutcome(
        status=OUTCOME_BY_REVIEW_STATUS[result.status],
        post_id=post.id if post else None,
        issues=result.issues,
    )
