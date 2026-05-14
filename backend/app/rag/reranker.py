from openai import OpenAI
from app.core.config import settings
import json

client = OpenAI(api_key=settings.openai_api_key)

def rerank_results(query: str, posts: list[dict], top_k: int = 3) -> list[dict]:
    """
    מדרג מחדש תוצאות חיפוש לפי רלוונטיות אמיתית לשאלה.
    
    למה לא לסמוך רק על RRF?
    כי RRF מודד דמיון טכני — וקטורים ומילות מפתח.
    Reranker מודד רלוונטיות סמנטית עמוקה יותר.
    
    דוגמה:
    שאלה: "DevOps בכיר עם 8 שנים"
    פוסט א: DevOps 6 שנים          → RRF גבוה, rerank בינוני
    פוסט ב: Senior DevOps 8 שנים   → RRF בינוני, rerank גבוה ✓
    """
    if not posts:
        return []

    # אם יש רק תוצאה אחת או שתיים — אין טעם לrerank
    if len(posts) <= 2:
        return posts[:top_k]

    # בנה את רשימת הפוסטים לדירוג
    posts_text = "\n\n".join([
        f"פוסט {i+1}:\n"
        f"תפקיד: {p['role']} | ניסיון: {p['years_experience']} שנים | "
        f"שכר: {p['salary']}₪ | מיקום: {p['location']}\n"
        f"תוכן: {p['raw_text']}"
        for i, p in enumerate(posts)
    ])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """אתה מומחה לשוק העבודה בהייטק הישראלי.
תפקידך לדרג פוסטים לפי רלוונטיות לשאלת השכר.

החזר אך ורק JSON array של מספרי הפוסטים מהכי רלוונטי לפחות רלוונטי.
דוגמה: [2, 1, 3]

קריטריונים לדירוג (לפי חשיבות):
1. התאמת תפקיד — האם הפוסט על אותו תפקיד?
2. התאמת ניסיון — האם רמת הניסיון דומה?
3. התאמת מיקום — האם המיקום רלוונטי?
4. עדכניות המידע — פוסטים ספציפיים עדיפים על כלליים"""
            },
            {
                "role": "user",
                "content": f"שאלה: {query}\n\nפוסטים לדירוג:\n{posts_text}"
            }
        ],
        temperature=0,
        max_tokens=50,
    )

    raw = response.choices[0].message.content.strip()

    try:
        ranking = json.loads(raw)
        # המר מספרי פוסטים (1-based) לindices (0-based)
        reranked = [posts[i-1] for i in ranking if 1 <= i <= len(posts)]
        return reranked[:top_k]
    except Exception:
        # fallback — החזר לפי סדר המקורי
        return posts[:top_k]