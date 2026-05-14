from openai import OpenAI
from app.core.config import settings
import json

client = OpenAI(api_key=settings.openai_api_key)

def expand_query(query: str) -> dict:
    """
    מחלץ מילות מפתח מהשאלה ומפריד לפי סוג וחשיבות.
    
    מחזיר:
    {
        "role": ["Data Scientist", "ML Engineer"],
        "tech": ["Python", "TensorFlow"],
        "location": ["תל אביב"]
    }
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """אתה עוזר לחיפוש מידע על שכר בהייטק הישראלי.
קבל שאלה והחזר JSON עם מילות מפתח מופרדות לפי קטגוריה.

החזר אך ורק JSON בפורמט הזה, ללא טקסט נוסף:
{
  "role": [],      // תפקידים ושמות משרות - הכי חשוב
  "tech": [],      // טכנולוגיות וכלים - חשוב
  "location": []   // מיקומים בלבד - פחות חשוב
}

חוקים:
- role: תפקידים בעברית ואנגלית, מקסימום 3
- tech: טכנולוגיות ספציפיות בלבד, מקסימום 3  
- location: מיקומים גיאוגרפיים בלבד, מקסימום 2
- אם קטגוריה לא רלוונטית — מערך ריק

דוגמה:
שאלה: "כמה מרוויח data scientist מתחיל?"
תשובה: {"role": ["data scientist", "ml engineer"], "tech": ["python", "machine learning"], "location": []}"""
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