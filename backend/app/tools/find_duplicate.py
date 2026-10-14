from typing import Literal

from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

NEAR_DUPLICATE_THRESHOLD = 0.95

EXACT_SQL = text(
    """
    SELECT id
    FROM salary_posts
    WHERE LOWER(TRIM(REGEXP_REPLACE(raw_text, '\\s+', ' ', 'g'))) = :normalized
    LIMIT 1
    """
)

NEAR_SQL = text(
    """
    SELECT id, 1 - (embedding <=> CAST(:embedding AS vector)) AS similarity
    FROM salary_posts
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> CAST(:embedding AS vector)
    LIMIT 1
    """
)


class DuplicateMatch(BaseModel):
    kind: Literal["exact", "near"]
    post_id: int
    similarity: float


def normalize_for_dedup(raw_text: str) -> str:
    return " ".join(raw_text.lower().split())


def _vector_literal(embedding: list[float]) -> str:
    return "[" + ",".join(str(value) for value in embedding) + "]"


def find_duplicate(
    db: Session,
    raw_text: str,
    embedding: list[float] | None = None,
) -> DuplicateMatch | None:
    exact = db.execute(
        EXACT_SQL, {"normalized": normalize_for_dedup(raw_text)}
    ).first()
    if exact:
        return DuplicateMatch(kind="exact", post_id=exact.id, similarity=1.0)

    if embedding is None:
        return None

    near = db.execute(NEAR_SQL, {"embedding": _vector_literal(embedding)}).first()
    if near and near.similarity >= NEAR_DUPLICATE_THRESHOLD:
        return DuplicateMatch(
            kind="near", post_id=near.id, similarity=round(near.similarity, 4)
        )
    return None
