import asyncio
from openai import AsyncOpenAI, APIConnectionError, RateLimitError
from app.core.config import settings
from app.core.exceptions import GenerationError, RetrievalError
from app.core.logging import get_logger
from app.core.query_logger import QueryTracker
from app.rag.retriever import search_similar_posts
from app.rag.reranker import rerank_results

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are an expert on the Israeli tech job market.
Answer salary questions based only on the real community data provided.

Rules:
- Only use the data provided. Never invent numbers.
- If there is not enough data — say so explicitly.
- Give a salary range, not a single number, when possible.
- Answer in Hebrew, clearly and directly.
- At the end, state how many posts you used."""


async def answer_salary_query(query: str) -> dict:
    if not query or not query.strip():
        raise ValueError("Empty query")

    tracker = QueryTracker(query)
    estimated_cost = 0.0

    logger.info(f"Query received: '{query}'")

    # Stage 1 — Retrieve
    try:
        with tracker.track_stage("retrieval"):
            candidates = await search_similar_posts(query, limit=10)

        tracker.posts_retrieved = len(candidates)
        tracker.retrieved_post_ids = [p["id"] for p in candidates]

    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        tracker.success = False
        tracker.error_message = str(e)
        tracker.save()
        raise RetrievalError("Failed to retrieve relevant data")

    if not candidates:
        logger.warning(f"No results for: '{query}'")
        tracker.save()
        return {
            "answer": "לא נמצאו נתונים רלוונטיים לשאלה שלך.",
            "sources": [],
            "posts_used": 0
        }

    # Stage 2 — Rerank
    try:
        with tracker.track_stage("reranking"):
            relevant_posts = await rerank_results(query, candidates, top_k=3)
    except Exception as e:
        logger.warning(f"Reranking failed, falling back: {e}")
        relevant_posts = candidates[:3]

    tracker.posts_after_rerank = len(relevant_posts)

    # Stage 3 — Generate
    try:
        with tracker.track_stage("generation"):
            context = _build_context(relevant_posts)

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Data:\n{context}\n\nQuestion: {query}"}
                ],
                temperature=0.3,
            )

        answer = response.choices[0].message.content
        usage = response.usage
        estimated_cost = tracker.add_tokens(
            usage.prompt_tokens,
            usage.completion_tokens
        )

    except RateLimitError:
        tracker.success = False
        tracker.error_message = "RateLimitError"
        tracker.save(estimated_cost)
        raise GenerationError("Server overloaded, please try again")

    except APIConnectionError:
        tracker.success = False
        tracker.error_message = "APIConnectionError"
        tracker.save(estimated_cost)
        raise GenerationError("AI server connection error")

    tracker.save(estimated_cost)

    return {
        "answer": answer,
        "sources": relevant_posts,
        "posts_used": len(relevant_posts)
    }


def _build_context(posts: list[dict]) -> str:
    lines = []
    for i, post in enumerate(posts, 1):
        lines.append(
            f"Post {i}:\n"
            f"Role: {post['role']} | "
            f"Experience: {post['years_experience']} years | "
            f"Salary: {post['salary']}₪ | "
            f"Location: {post['location']}\n"
            f"Quote: {post['raw_text']}\n"
        )
    return "\n".join(lines)