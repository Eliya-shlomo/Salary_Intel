from openai import OpenAI
from app.core.config import settings
from app.core.logging import get_logger
import json

logger = get_logger(__name__)
client = OpenAI(api_key=settings.openai_api_key)

ROLES = [
    "Frontend Developer", "Backend Developer", "Fullstack Developer",
    "DevOps Engineer", "Data Scientist", "Data Engineer",
    "ML Engineer", "Team Lead", "Product Manager",
    "QA Engineer", "Mobile Developer", "Cyber Security",
    "Solution Architect", "SRE", "Cloud Engineer",
]

LOCATIONS = ["תל אביב", "רמת גן", "הרצליה", "פתח תקווה",
             "באר שבע", "חיפה", "ירושלים", "רעננה", "נתניה"]

STAGES = ["Startup", "Series A", "Series B", "Series C", "Enterprise"]


def generate_salary_posts(count: int = 50) -> list[str]:
    """
    מייצר פוסטים סינתטיים אמיתיים לפי פרמטרים.
    כל batch מייצר 10 פוסטים בקריאה אחת.
    """
    all_posts = []
    batches = count // 10

    for batch in range(batches):
        logger.info(f"מייצר batch {batch+1}/{batches}...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """אתה מדמה פוסטים אמיתיים מקבוצות פייסבוק ישראליות על שכר בהייטק.

הפוסטים צריכים להיות:
- בעברית מדוברת, לא פורמלית
- עם שכר ריאלי לפי שוק ישראל 2024
- מגוונים — שאלות, עדכונים, השוואות
- עם פרטים ספציפיים — ניסיון, מיקום, שלב חברה
- לפעמים עם שגיאות כתיב קלות (כמו בפוסטים אמיתיים)

החזר JSON array של 10 פוסטים. רק JSON, ללא טקסט נוסף.
פורמט: ["פוסט 1", "פוסט 2", ...]"""
                },
                {
                    "role": "user",
                    "content": f"""צור 10 פוסטים מגוונים על שכר בהייטק הישראלי.

השתמש בתפקידים אלה (בחר אקראי): {', '.join(ROLES)}
מיקומים: {', '.join(LOCATIONS)}
שלבי חברה: {', '.join(STAGES)}

וודא גיוון:
- תפקידים שונים בכל פוסט
- שכר ריאלי לפי ניסיון (junior: 15-25K, mid: 25-40K, senior: 40-60K+)
- חלק שאלות ("מה דעתכם על ההצעה?")
- חלק עדכונים ("רוצה לשתף את הקהילה")"""
                }
            ],
            temperature=0.8,  # גבוה יותר = יצירתי יותר
            max_tokens=2000,
        )

        raw = response.choices[0].message.content.strip()

        try:
            posts = json.loads(raw)
            all_posts.extend(posts)
            logger.info(f"✓ batch {batch+1}: {len(posts)} פוסטים")
        except json.JSONDecodeError:
            logger.warning(f"batch {batch+1} החזיר JSON לא תקין")

    return all_posts