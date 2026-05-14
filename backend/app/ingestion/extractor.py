from openai import OpenAI
from app.core.config import settings
from app.core.logging import get_logger
import json

logger = get_logger(__name__)
client = OpenAI(api_key=settings.openai_api_key)

MIN_SALARY = 3000
MAX_SALARY = 300000


def extract_salary_data(raw_text: str) -> dict:
    """
    מחלץ מידע מובנה מפוסט גולמי.

    קלט:  "מפתח React 4 שנים, קיבלתי 28K בתל אביב"
    פלט:  {"role": "Frontend Developer", "salary": 28000, ...}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """אתה מומחה לשוק העבודה בהייטק הישראלי.
חלץ מידע מובנה מפוסטים על שכר.

החזר אך ורק JSON בפורמט הזה, ללא טקסט נוסף:
{
  "role": "שם התפקיד באנגלית (למשל: Frontend Developer, DevOps Engineer)",
  "salary": מספר בשקלים או null,
  "years_experience": מספר שנות ניסיון או null,
  "company_stage": "Startup/Series A/Series B/Enterprise/Unknown",
  "location": "עיר בעברית או null",
  "is_salary_post": true/false
}

חוקים:
- role תמיד באנגלית
- salary כמספר בלבד ללא סימני מטבע (28000 לא 28K)
- אם המידע לא מופיע — null
- is_salary_post: האם הפוסט עוסק בשכר?"""
            },
            {
                "role": "user",
                "content": raw_text
            }
        ],
        temperature=0,
        max_tokens=150,
    )

    raw = response.choices[0].message.content.strip()

    try:
        data = json.loads(raw)

        # וידוא שכר הגיוני
        salary = data.get("salary")
        if salary is not None:
            if not isinstance(salary, (int, float)) or salary < MIN_SALARY or salary > MAX_SALARY:
                logger.warning(f"שכר לא הגיוני: {salary} — מאפס")
                salary = None

        return {
            "role": data.get("role"),
            "salary": salary,
            "years_experience": data.get("years_experience"),
            "company_stage": data.get("company_stage"),
            "location": data.get("location"),
            "is_salary_post": data.get("is_salary_post", True),
        }

    except json.JSONDecodeError as e:
        logger.warning(f"Extractor החזיר JSON לא תקין: {e}")
        return {
            "role": None,
            "salary": None,
            "years_experience": None,
            "company_stage": None,
            "location": None,
            "is_salary_post": False,
        }