from langchain.tools import tool

from app.db.database import SessionLocal
from app.rag.retriever import search_similar_posts
from app.tools.compute_stats import PayBasis, compute_stats
from app.tools.normalize_role import CanonicalRole

SEARCH_LIMIT = 5


@tool
def salary_stats(
    role: CanonicalRole | None = None,
    pay_basis: PayBasis | None = None,
    min_years: float | None = None,
    max_years: float | None = None,
) -> dict:
    """Get monthly salary percentiles (p25, p50, p75) in NIS for approved posts.
    Use it for questions like "what is the typical salary of a devops engineer".
    The result includes n, the number of posts used. With fewer than 5 posts
    no percentiles are returned, and the note explains which filter to remove."""
    with SessionLocal() as db:
        return compute_stats(
            db,
            role=role,
            pay_basis=pay_basis,
            min_years=min_years,
            max_years=max_years,
        ).model_dump()


@tool
async def search_posts(query: str) -> list[dict]:
    """Search salary posts that are relevant to a free-text question.
    Returns up to 5 compact results: id, role, years_experience, monthly salary in NIS,
    location and company_stage. Use it to find examples, not to compute statistics."""
    posts = await search_similar_posts(query, limit=SEARCH_LIMIT)
    return [
        {
            "id": p["id"],
            "role": p["role"],
            "years_experience": p["years_experience"],
            "salary": p["salary"],
            "location": p["location"],
            "company_stage": p["company_stage"],
        }
        for p in posts
    ]
