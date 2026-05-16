from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
import json

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def rerank_results(query: str, posts: list[dict], top_k: int = 3) -> list[dict]:
    """
    Re-ranks search results by true relevance to the query.
    GPT reads all candidates and returns the most relevant order.
    """
    if not posts:
        return []

    if len(posts) <= 2:
        return posts[:top_k]

    posts_text = "\n\n".join([
        f"Post {i+1}:\n"
        f"Role: {p['role']} | Experience: {p['years_experience']} years | "
        f"Salary: {p['salary']}₪\n"
        f"Content: {p['raw_text']}"
        for i, p in enumerate(posts)
    ])

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert on the Israeli tech job market.
Rank the posts by relevance to the salary question.

Return ONLY a JSON array of post numbers from most to least relevant.
Example: [2, 1, 3]

Ranking criteria (by importance):
1. Role match — is the post about the same role?
2. Experience match — is the experience level similar?
3. Location match — is the location relevant?
4. Data specificity — specific posts are better than general ones"""
                },
                {
                    "role": "user",
                    "content": f"Question: {query}\n\nPosts to rank:\n{posts_text}"
                }
            ],
            temperature=0,
            max_tokens=50,
        )

        raw = response.choices[0].message.content.strip()
        ranking = json.loads(raw)

        if not isinstance(ranking, list):
            raise ValueError("Invalid reranker response")

        reranked = []
        seen_ids = set()
        for i in ranking:
            if 1 <= i <= len(posts):
                post = posts[i-1]
                if post["id"] not in seen_ids:
                    seen_ids.add(post["id"])
                    reranked.append(post)

        if not reranked:
            raise ValueError("Empty ranking list")

        logger.info(f"Reranking successful: {[p['role'] for p in reranked[:top_k]]}")
        return reranked[:top_k]

    except json.JSONDecodeError as e:
        logger.warning(f"Reranker returned invalid JSON: {e} | falling back")
        return posts[:top_k]

    except Exception as e:
        logger.warning(f"Reranking failed: {e} | falling back")
        return posts[:top_k]