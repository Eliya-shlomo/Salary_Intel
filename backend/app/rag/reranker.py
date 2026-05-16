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

    # Build structured posts text
    posts_text = "\n".join([
        f"Post {i+1}: Role: {p['role']} | "
        f"Salary: {p['salary']}₪ | "
        f"Experience: {p['years_experience']} years | "
        f"Location: {p['location']}"
        for i, p in enumerate(posts)
    ])

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You rank salary posts by relevance to a question. Return ONLY a JSON array of integers like [2, 1, 3]. No explanation, no markdown, just the array."
                },
                {
                    "role": "user",
                    "content": f"Question: {query}\n\n{posts_text}\n\nReturn the ranking array:"
                }
            ],
            temperature=0,
            max_tokens=50,
        )

        raw = response.choices[0].message.content.strip()
        ranking = json.loads(raw)

        if not isinstance(ranking, list) or len(ranking) == 0:
            raise ValueError(f"Invalid ranking: {raw}")

        # Deduplicate and validate
        reranked = []
        seen_ids = set()
        for i in ranking:
            if 1 <= i <= len(posts):
                post = posts[i-1]
                if post["id"] not in seen_ids:
                    seen_ids.add(post["id"])
                    reranked.append(post)

        if not reranked:
            raise ValueError("Empty after dedup")

        logger.info(f"Reranking successful: {[p['role'] for p in reranked[:top_k]]}")
        return reranked[:top_k]

    except json.JSONDecodeError as e:
        logger.warning(f"Reranker invalid JSON: '{raw}' | {e} | falling back")
        return posts[:top_k]

    except Exception as e:
        logger.warning(f"Reranking failed: {e} | falling back")
        return posts[:top_k]