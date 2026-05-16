from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
import json

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)

MIN_SALARY = 3000
MAX_SALARY = 300000


async def extract_salary_data(raw_text: str) -> dict:
    """
    Extracts structured data from a raw salary post using GPT.
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are an expert on the Israeli tech job market.
Extract structured data from salary posts.

Return ONLY a JSON object, no extra text:
{
  "role": "job title in English (e.g. Frontend Developer, DevOps Engineer)",
  "salary": number in shekels or null,
  "years_experience": number of years or null,
  "company_stage": "Startup/Series A/Series B/Enterprise/Unknown",
  "location": "city in Hebrew or null",
  "is_salary_post": true/false
}

Rules:
- role always in English
- salary as number only, no currency symbols (28000 not 28K)
- if info not present — null
- is_salary_post: is this post about salary?"""
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

        salary = data.get("salary")
        if salary is not None:
            if not isinstance(salary, (int, float)) or salary < MIN_SALARY or salary > MAX_SALARY:
                logger.warning(f"Invalid salary: {salary} — setting to None")
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
        logger.warning(f"Extractor returned invalid JSON: {e}")
        return {
            "role": None,
            "salary": None,
            "years_experience": None,
            "company_stage": None,
            "location": None,
            "is_salary_post": False,
        }