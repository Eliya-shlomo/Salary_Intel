from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
import json

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def expand_query(query: str) -> dict:
    """
    Sends the query to GPT and returns structured keywords by category.

    Example:
    "כמה מרוויח DevOps בכיר?"
    → {"role": ["devops", "devops engineer"], "tech": ["aws", "docker"], "location": []}
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a helper for searching Israeli tech salary data.
Given a question, return relevant keywords separated by category.

Return ONLY a JSON object, no extra text:
{
  "role": [],      // job titles in Hebrew and English — most important
  "tech": [],      // specific technologies only — important
  "location": []   // geographic locations only — less important
}

Rules:
- role: job titles in Hebrew and English, max 3
- tech: specific technologies only, max 3
- location: geographic locations only, max 2
- If a category is not relevant — empty array"""
            },
            {
                "role": "user",
                "content": query
            }
        ],
        temperature=0,
        max_tokens=150,
    )

    raw = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw)
        return {
            "role": [k.lower() for k in parsed.get("role", [])],
            "tech": [k.lower() for k in parsed.get("tech", [])],
            "location": [k.lower() for k in parsed.get("location", [])],
        }
    except Exception:
        return {"role": [], "tech": [], "location": []}