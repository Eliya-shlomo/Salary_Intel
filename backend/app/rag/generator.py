from openai import OpenAI, APIConnectionError, RateLimitError
from app.core.config import settings
from app.core.exceptions import GenerationError, RetrievalError
from app.core.logging import get_logger
from app.rag.retriever import search_similar_posts
from app.rag.reranker import rerank_results

logger = get_logger(__name__)
client = OpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """אתה מומחה לשוק העבודה בהייטק הישראלי.
אתה עונה על שאלות שכר בהתבסס אך ורק על נתונים אמיתיים מהקהילה.

חוקים:
- ענה רק לפי הנתונים שסופקו. אל תמציא מספרים.
- אם אין מספיק נתונים — אמור זאת בפירוש.
- ציין טווח שכר ולא מספר בודד כשאפשר.
- ענה בעברית, בצורה ישירה וברורה.
- בסוף כל תשובה ציין כמה פוסטים השתמשת בהם."""


def answer_salary_query(query: str) -> dict:
    if not query or not query.strip():
        raise ValueError("שאלה ריקה")

    logger.info(f"שאלה התקבלה: '{query}'")

    # שלב 1 — Retrieve
    try:
        candidates = search_similar_posts(query, limit=10)
    except Exception as e:
        logger.error(f"שגיאת retrieval: {e}")
        raise RetrievalError("נכשל בחיפוש נתונים רלוונטיים")

    if not candidates:
        logger.warning(f"לא נמצאו תוצאות: '{query}'")
        return {
            "answer": "לא נמצאו נתונים רלוונטיים לשאלה שלך.",
            "sources": [],
            "posts_used": 0
        }

    logger.info(f"נמצאו {len(candidates)} מועמדים")

    # שלב 2 — Rerank
    try:
        relevant_posts = rerank_results(query, candidates, top_k=3)
    except Exception as e:
        logger.warning(f"Reranking נכשל, fallback לסדר מקורי: {e}")
        relevant_posts = candidates[:3]

    logger.info(f"אחרי reranking: {len(relevant_posts)} פוסטים")

    # שלב 3 — Generate
    try:
        context = _build_context(relevant_posts)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"נתונים:\n{context}\n\nשאלה: {query}"}
            ],
            temperature=0.3,
        )

        answer = response.choices[0].message.content
        logger.info(f"תשובה נוצרה | {len(answer)} תווים")

        return {
            "answer": answer,
            "sources": relevant_posts,
            "posts_used": len(relevant_posts)
        }

    except RateLimitError:
        logger.error("OpenAI Rate Limit בזמן generation")
        raise GenerationError("עומס על השרת, נסה שוב בעוד מספר שניות")

    except APIConnectionError:
        logger.error("חיבור ל-OpenAI נכשל בזמן generation")
        raise GenerationError("בעיית תקשורת עם שרת ה-AI")

    except Exception as e:
        logger.error(f"שגיאה לא צפויה ב-generation: {e}")
        raise GenerationError("שגיאה ביצירת התשובה")


def _build_context(posts: list[dict]) -> str:
    lines = []
    for i, post in enumerate(posts, 1):
        lines.append(
            f"פוסט {i}:\n"
            f"תפקיד: {post['role']} | "
            f"ניסיון: {post['years_experience']} שנים | "
            f"שכר: {post['salary']}₪ | "
            f"מיקום: {post['location']}\n"
            f"ציטוט: {post['raw_text']}\n"
        )
    return "\n".join(lines)