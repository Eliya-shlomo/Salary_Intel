from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.openai_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

def get_embedding(text: str) -> list[float]:
    """
    ממיר טקסט לוקטור באמצעות OpenAI.
    text-embedding-3-small: זול, מהיר, ומצוין לעברית.
    """
    text = text.replace("\n", " ").strip()
    
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    
    return response.data[0].embedding

def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    ממיר רשימת טקסטים לוקטורים בקריאה אחת ל-API.
    הרבה יותר יעיל מלקרוא get_embedding בלולאה.
    """
    texts = [t.replace("\n", " ").strip() for t in texts]
    
    response = client.embeddings.create(
        input=texts,
        model=EMBEDDING_MODEL
    )
    
    return [item.embedding for item in response.data]
