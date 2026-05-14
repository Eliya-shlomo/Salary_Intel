from openai import OpenAI, APIConnectionError, RateLimitError, APIStatusError
from app.core.config import settings
from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger

logger = get_logger(__name__)
client = OpenAI(api_key=settings.openai_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536

def get_embedding(text: str) -> list[float]:
    text = text.replace("\n", " ").strip()

    if not text:
        raise EmbeddingError("טקסט ריק — לא ניתן ליצור embedding")

    try:
        logger.info(f"יוצר embedding | {len(text)} תווים")
        response = client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding

    except RateLimitError:
        logger.error("OpenAI Rate Limit — יותר מדי קריאות")
        raise EmbeddingError("עומס על השרת, נסה שוב בעוד מספר שניות")

    except APIConnectionError:
        logger.error("לא ניתן להתחבר ל-OpenAI API")
        raise EmbeddingError("בעיית תקשורת עם שרת ה-AI")

    except APIStatusError as e:
        logger.error(f"OpenAI API error: {e.status_code}")
        raise EmbeddingError(f"שגיאת API: {e.status_code}")


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    texts = [t.replace("\n", " ").strip() for t in texts]

    try:
        response = client.embeddings.create(
            input=texts,
            model=EMBEDDING_MODEL
        )
        return [item.embedding for item in response.data]

    except RateLimitError:
        raise EmbeddingError("עומס על השרת, נסה שוב בעוד מספר שניות")

    except APIConnectionError:
        raise EmbeddingError("בעיית תקשורת עם שרת ה-AI")