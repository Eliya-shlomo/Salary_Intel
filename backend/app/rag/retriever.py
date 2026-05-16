import asyncio
from sqlalchemy import text
from app.db.database import SessionLocal
from app.rag.embeddings import get_embedding
from app.rag.query_parser import expand_query
from app.core.logging import get_logger
import re

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.25
RRF_K = 60

FIELD_WEIGHTS = {
    "role": 3,
    "tech": 2,
    "location": 1,
}


async def search_similar_posts(
    query: str,
    limit: int = 5,
    threshold: float = SIMILARITY_THRESHOLD
) -> list[dict]:
    """
    Hybrid Search with async parallelism.
    embed + expand run concurrently — saves ~500ms per query.
    """
    # Run embedding and query expansion in parallel
    query_embedding, keywords = await asyncio.gather(
        get_embedding(query),
        expand_query(query)
    )

    logger.info(f"🔑 role: {keywords['role']}")
    logger.info(f"🔑 tech: {keywords['tech']}")
    logger.info(f"📍 location: {keywords['location']}")

    db = SessionLocal()
    try:
        keyword_conditions = _build_weighted_keyword_conditions(keywords)

        results = db.execute(
            text(f"""
                WITH semantic AS (
                    SELECT
                        id,
                        1 - (embedding <=> CAST(:embedding AS vector)) AS similarity,
                        ROW_NUMBER() OVER (
                            ORDER BY embedding <=> CAST(:embedding AS vector)
                        ) AS rank
                    FROM salary_posts
                    WHERE 1 - (embedding <=> CAST(:embedding AS vector)) > :threshold
                ),
                keyword AS (
                    {keyword_conditions}
                ),
                rrf AS (
                    SELECT
                        COALESCE(s.id, k.id) AS id,
                        COALESCE(1.0 / (:rrf_k + s.rank), 0) +
                        COALESCE(1.0 / (:rrf_k + k.rank), 0) AS rrf_score,
                        COALESCE(s.similarity, 0) AS similarity
                    FROM semantic s
                    FULL OUTER JOIN keyword k ON s.id = k.id
                )
                SELECT
                    p.id, p.raw_text, p.role, p.years_experience,
                    p.salary, p.location, p.company_stage,
                    r.similarity, r.rrf_score
                FROM rrf r
                JOIN salary_posts p ON p.id = r.id
                ORDER BY r.rrf_score DESC
                LIMIT :limit
            """),
            {
                "embedding": str(query_embedding),
                "threshold": threshold,
                "rrf_k": RRF_K,
                "limit": limit,
            }
        ).fetchall()

        return [
            {
                "id": r.id,
                "raw_text": r.raw_text,
                "role": r.role,
                "years_experience": r.years_experience,
                "salary": r.salary,
                "location": r.location,
                "company_stage": r.company_stage,
                "similarity": round(r.similarity, 3),
                "rrf_score": round(r.rrf_score, 4),
            }
            for r in results
        ]
    finally:
        db.close()


def _sanitize_keyword(kw: str) -> str:
    """Remove dangerous characters before inserting into dynamic SQL."""
    cleaned = re.sub(r"[^\w\s]", "", kw)
    return cleaned[:50].strip()


def _build_weighted_keyword_conditions(keywords: dict) -> str:
    has_any = any(keywords[k] for k in keywords)
    if not has_any:
        return "SELECT NULL::int AS id, NULL::int AS rank WHERE false"

    score_parts = []

    for kw in keywords["role"]:
        safe_kw = _sanitize_keyword(kw)
        if not safe_kw:
            continue
        score_parts.append(
            f"CASE WHEN LOWER(role) LIKE '%{safe_kw}%' "
            f"THEN {FIELD_WEIGHTS['role']} ELSE 0 END"
        )

    for kw in keywords["tech"]:
        safe_kw = _sanitize_keyword(kw)
        if not safe_kw:
            continue
        score_parts.append(
            f"CASE WHEN LOWER(role) LIKE '%{safe_kw}%' "
            f"OR LOWER(company_stage) LIKE '%{safe_kw}%' "
            f"THEN {FIELD_WEIGHTS['tech']} ELSE 0 END"
        )

    for kw in keywords["location"]:
        safe_kw = _sanitize_keyword(kw)
        if not safe_kw:
            continue
        score_parts.append(
            f"CASE WHEN LOWER(location) LIKE '%{safe_kw}%' "
            f"THEN {FIELD_WEIGHTS['location']} ELSE 0 END"
        )

    if not score_parts:
        return "SELECT NULL::int AS id, NULL::int AS rank WHERE false"

    score_expr = " + ".join(score_parts)

    return f"""
        SELECT
            id,
            ROW_NUMBER() OVER (ORDER BY weighted_score DESC) AS rank
        FROM (
            SELECT id, ({score_expr}) AS weighted_score
            FROM salary_posts
            WHERE ({score_expr}) > 0
        ) scored
    """