import asyncio
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.exceptions import EmbeddingError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Async client — runs without blocking
client = AsyncOpenAI(api_key=settings.openai_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIM = 1536


async def get_embedding(text: str) -> list[float]:
    text = text.replace("\n", " ").strip()

    if not text:
        raise EmbeddingError("Empty text — cannot create embedding")

    try:
        logger.info(f"Creating embedding | {len(text)} chars")
        response = await client.embeddings.create(
            input=text,
            model=EMBEDDING_MODEL
        )
        return response.data[0].embedding

    except Exception as e:
        logger.error(f"Embedding error: {e}")
        raise EmbeddingError(f"Failed to create embedding: {e}")


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    texts = [t.replace("\n", " ").strip() for t in texts]

    try:
        response = await client.embeddings.create(
            input=texts,
            model=EMBEDDING_MODEL
        )
        return [item.embedding for item in response.data]

    except Exception as e:
        raise EmbeddingError(f"Batch embedding failed: {e}")