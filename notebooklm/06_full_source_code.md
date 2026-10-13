# קוד המקור המלא — Salary Intel (מסמך 06)

> קובץ זה מרכז את כל קוד המקור של הפרויקט במקום אחד, כדי ש-NotebookLM יוכל לענות על שאלות שמצריכות קריאה בקוד עצמו.
> **הערה:** קבצי `.env` ומפתחות API אינם כלולים כאן במכוון.

---


## `docker-compose.yml`

```yaml
services:
  db:
    image: pgvector/pgvector:pg16
    platform: linux/arm64
    container_name: salary_intel_db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: salary_intel
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    platform: linux/arm64
    container_name: salary_intel_redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  api:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: salary_intel_api
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/salary_intel
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      REDIS_URL: redis://redis:6379
      API_KEY: ${API_KEY}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend/app:/app/app

volumes:
  postgres_data:
```


## `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```


## `backend/requirements.txt`

```text
fastapi==0.111.0
uvicorn==0.29.0
psycopg2-binary==2.9.9
pgvector==0.2.5
sqlalchemy==2.0.30
openai>=1.0.0
httpx>=0.27.0
python-dotenv==1.0.1
pydantic-settings==2.2.1
slowapi==0.1.9
redis==5.0.4
```


## `backend/render.yaml`

```yaml
services:
  - type: web
    name: salary-intel-api
    runtime: docker
    dockerfilePath: ./backend/Dockerfile
    dockerContext: ./backend
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: DATABASE_URL
        sync: false
    healthCheckPath: /health
```


## `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.config import settings
from app.core.logging import get_logger
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.db.database import check_connection
from app.api.routes import router

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug
)

# Rate Limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health_check():
    db_ok = check_connection()
    return {
        "status": "ok",
        "app": settings.app_name,
        "database": "connected" if db_ok else "error"
    }
```


## `backend/app/api/routes.py`

```python
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from app.rag.generator import answer_salary_query
from app.ingestion.ingestor import ingest_post
from app.core.exceptions import SalaryIntelError
from app.core.logging import get_logger
from app.core.rate_limiter import limiter
from app.core.security import verify_api_key

logger = get_logger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str
    posts_used: int
    sources: list[dict]


class IngestRequest(BaseModel):
    raw_text: str
    role: str | None = None
    years_experience: float | None = None
    salary: float | None = None
    company_stage: str | None = None
    location: str | None = None
    source: str = "manual"


@router.post("/query", response_model=QueryResponse)
@limiter.limit("10/minute")
async def query_salary(
    request: Request,
    body: QueryRequest,
    api_key: str = Depends(verify_api_key)
):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Empty query")

    try:
        result = await answer_salary_query(body.query)
        return QueryResponse(**result)

    except SalaryIntelError as e:
        logger.warning(f"SalaryIntelError: {e}")
        raise HTTPException(status_code=503, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/ingest")
@limiter.limit("5/minute")
async def ingest_new_post(
    request: Request,
    body: IngestRequest,
    api_key: str = Depends(verify_api_key)
):
    try:
        post = ingest_post(**body.model_dump())
        return {"id": post.id, "message": "Saved successfully"}

    except SalaryIntelError as e:
        logger.warning(f"Ingest error: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected ingest error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error saving post")


@router.get("/stats")
@limiter.limit("30/minute")
async def get_stats(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    try:
        from app.db.database import SessionLocal
        from app.db.models import SalaryPost
        db = SessionLocal()
        try:
            count = db.query(SalaryPost).count()
            return {"total_posts": count}
        finally:
            db.close()

    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail="Error loading stats")
```


## `backend/app/core/config.py`

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    openai_api_key: str
    redis_url: str = "redis://localhost:6379"
    api_key: str = "dev-secret-key"  
    app_name: str = "Salary Intel"
    debug: bool = False
    port: int = 8000

    class Config:
        env_file = (
            "app/.env",
            "../app/.env",
            ".env",
            "../.env",
        )

settings = Settings()
```


## `backend/app/core/security.py`

```python
from fastapi import Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    FastAPI Dependency — runs before every protected endpoint.
    If header is missing or doesn't match — returns 401.
    If valid — allows request to continue.
    """
    if not api_key or api_key != settings.api_key:
        logger.warning("Access attempt with invalid API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return api_key
```


## `backend/app/core/rate_limiter.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
)

def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    client_ip = get_remote_address(request)
    logger.warning(f"Rate limit חרג | IP: {client_ip}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "יותר מדי בקשות. נסה שוב בעוד דקה.",
            "retry_after": "60 seconds"
        }
    )
```


## `backend/app/core/query_logger.py`

```python
import time
from contextlib import contextmanager
from app.db.database import SessionLocal
from app.db.models import QueryLog
from app.core.logging import get_logger

logger = get_logger(__name__)

# GPT-4o-mini pricing (per 1M tokens)
COST_PER_INPUT_TOKEN = 0.00000015   # $0.15 per 1M
COST_PER_OUTPUT_TOKEN = 0.0000006   # $0.60 per 1M


class QueryTracker:
    """
    Tracks latency and cost for a single query across all pipeline stages.
    Usage: create once per query, call start/end for each stage.
    """

    def __init__(self, query: str):
        self.query = query
        self.start_time = time.time()

        self.latency_retrieval: float | None = None
        self.latency_reranking: float | None = None
        self.latency_generation: float | None = None

        self.posts_retrieved: int = 0
        self.posts_after_rerank: int = 0
        self.retrieved_post_ids: list[int] = []

        self.tokens_used: int = 0
        self.success: bool = True
        self.error_message: str | None = None

    @contextmanager
    def track_stage(self, stage: str):
        """Context manager to track latency of a single stage."""
        t = time.time()
        try:
            yield
        finally:
            elapsed = round(time.time() - t, 3)
            setattr(self, f"latency_{stage}", elapsed)
            logger.info(f"Stage '{stage}' completed in {elapsed}s")

    def add_tokens(self, input_tokens: int, output_tokens: int):
        """Track token usage and estimate cost."""
        self.tokens_used += input_tokens + output_tokens
        cost = (input_tokens * COST_PER_INPUT_TOKEN) + (output_tokens * COST_PER_OUTPUT_TOKEN)
        return round(cost, 6)

    def save(self, estimated_cost_usd: float = 0.0):
        """Save the completed query log to the database."""
        total = round(time.time() - self.start_time, 3)

        db = SessionLocal()
        try:
            log = QueryLog(
                query=self.query,
                latency_retrieval=self.latency_retrieval,
                latency_reranking=self.latency_reranking,
                latency_generation=self.latency_generation,
                latency_total=total,
                posts_retrieved=self.posts_retrieved,
                posts_after_rerank=self.posts_after_rerank,
                retrieved_post_ids=self.retrieved_post_ids,
                tokens_used=self.tokens_used,
                estimated_cost_usd=estimated_cost_usd,
                success=self.success,
                error_message=self.error_message,
            )
            db.add(log)
            db.commit()
            logger.info(
                f"Query logged | total={total}s | "
                f"tokens={self.tokens_used} | "
                f"cost=${estimated_cost_usd}"
            )
        except Exception as e:
            logger.error(f"Failed to save query log: {e}")
        finally:
            db.close()
```


## `backend/app/core/exceptions.py`

```python
class SalaryIntelError(Exception):
    """Base exception לכל שגיאות הפרויקט"""
    pass


class EmbeddingError(SalaryIntelError):
    """נכשל ביצירת embedding"""
    pass


class RetrievalError(SalaryIntelError):
    """נכשל בחיפוש במסד"""
    pass


class GenerationError(SalaryIntelError):
    """נכשל ביצירת תשובה"""
    pass


class DatabaseError(SalaryIntelError):
    """שגיאת מסד נתונים"""
    pass
```


## `backend/app/core/logging.py`

```python
import logging
import sys

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
```


## `backend/app/db/database.py`

```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_connection():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return True
```


## `backend/app/db/models.py`

```python
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db.database import Base


class SalaryPost(Base):
    __tablename__ = "salary_posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str | None] = mapped_column(String(100))
    years_experience: Mapped[float | None] = mapped_column(Float)
    salary: Mapped[float | None] = mapped_column(Float)
    company_stage: Mapped[str | None] = mapped_column(String(50))
    location: Mapped[str | None] = mapped_column(String(100))
    embedding: Mapped[list | None] = mapped_column(Vector(1536))
    source: Mapped[str | None] = mapped_column(String(100))
    post_date: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # The query itself
    query: Mapped[str] = mapped_column(Text, nullable=False)

    # Latency per stage (in seconds)
    latency_retrieval: Mapped[float | None] = mapped_column(Float)
    latency_reranking: Mapped[float | None] = mapped_column(Float)
    latency_generation: Mapped[float | None] = mapped_column(Float)
    latency_total: Mapped[float | None] = mapped_column(Float)

    # Results
    posts_retrieved: Mapped[int | None] = mapped_column(Integer)
    posts_after_rerank: Mapped[int | None] = mapped_column(Integer)
    retrieved_post_ids: Mapped[list | None] = mapped_column(JSON)

    # Cost estimation
    tokens_used: Mapped[int | None] = mapped_column(Integer)
    estimated_cost_usd: Mapped[float | None] = mapped_column(Float)

    # Status
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```


## `backend/app/db/init_db.py`

```python
from app.db.database import engine
from app.db.models import Base
from sqlalchemy import text

def init_db():
    # הפעל את תוסף pgvector
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # צור את כל הטבלאות
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")

if __name__ == "__main__":
    init_db()
```


## `backend/app/rag/embeddings.py`

```python
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
```


## `backend/app/rag/query_parser.py`

```python
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
```


## `backend/app/rag/retriever.py`

```python
import asyncio
from sqlalchemy import text
from app.db.database import SessionLocal
from app.rag.embeddings import get_embedding
from app.rag.query_parser import expand_query
from app.core.logging import get_logger
import re

logger = get_logger(__name__)

SIMILARITY_THRESHOLD = 0.25
RRF_K = 60

FIELD_WEIGHTS = {
    "role": 3,
    "tech": 2,
    "location": 1,
}


async def search_similar_posts(
    query: str,
    limit: int = 5,
    threshold: float = SIMILARITY_THRESHOLD
) -> list[dict]:
    """
    Hybrid Search with async parallelism.
    embed + expand run concurrently — saves ~500ms per query.
    """
    # Run embedding and query expansion in parallel
    query_embedding, keywords = await asyncio.gather(
        get_embedding(query),
        expand_query(query)
    )

    logger.info(f"🔑 role: {keywords['role']}")
    logger.info(f"🔑 tech: {keywords['tech']}")
    logger.info(f"📍 location: {keywords['location']}")

    db = SessionLocal()
    try:
        keyword_conditions = _build_weighted_keyword_conditions(keywords)

        results = db.execute(
            text(f"""
                WITH semantic AS (
                    SELECT
                        id,
                        1 - (embedding <=> CAST(:embedding AS vector)) AS similarity,
                        ROW_NUMBER() OVER (
                            ORDER BY embedding <=> CAST(:embedding AS vector)
                        ) AS rank
                    FROM salary_posts
                    WHERE 1 - (embedding <=> CAST(:embedding AS vector)) > :threshold
                ),
                keyword AS (
                    {keyword_conditions}
                ),
                rrf AS (
                    SELECT
                        COALESCE(s.id, k.id) AS id,
                        COALESCE(1.0 / (:rrf_k + s.rank), 0) +
                        COALESCE(1.0 / (:rrf_k + k.rank), 0) AS rrf_score,
                        COALESCE(s.similarity, 0) AS similarity
                    FROM semantic s
                    FULL OUTER JOIN keyword k ON s.id = k.id
                )
                SELECT
                    p.id, p.raw_text, p.role, p.years_experience,
                    p.salary, p.location, p.company_stage,
                    r.similarity, r.rrf_score
                FROM rrf r
                JOIN salary_posts p ON p.id = r.id
                ORDER BY r.rrf_score DESC
                LIMIT :limit
            """),
            {
                "embedding": str(query_embedding),
                "threshold": threshold,
                "rrf_k": RRF_K,
                "limit": limit,
            }
        ).fetchall()

        return [
            {
                "id": r.id,
                "raw_text": r.raw_text,
                "role": r.role,
                "years_experience": r.years_experience,
                "salary": r.salary,
                "location": r.location,
                "company_stage": r.company_stage,
                "similarity": round(r.similarity, 3),
                "rrf_score": round(r.rrf_score, 4),
            }
            for r in results
        ]
    finally:
        db.close()


def _sanitize_keyword(kw: str) -> str:
    """Remove dangerous characters before inserting into dynamic SQL."""
    cleaned = re.sub(r"[^\w\s]", "", kw)
    return cleaned[:50].strip()


def _build_weighted_keyword_conditions(keywords: dict) -> str:
    has_any = any(keywords[k] for k in keywords)
    if not has_any:
        return "SELECT NULL::int AS id, NULL::int AS rank WHERE false"

    score_parts = []

    for kw in keywords["role"]:
        safe_kw = _sanitize_keyword(kw)
        if not safe_kw:
            continue
        score_parts.append(
            f"CASE WHEN LOWER(role) LIKE '%{safe_kw}%' "
            f"THEN {FIELD_WEIGHTS['role']} ELSE 0 END"
        )

    for kw in keywords["tech"]:
        safe_kw = _sanitize_keyword(kw)
        if not safe_kw:
            continue
        score_parts.append(
            f"CASE WHEN LOWER(role) LIKE '%{safe_kw}%' "
            f"OR LOWER(company_stage) LIKE '%{safe_kw}%' "
            f"THEN {FIELD_WEIGHTS['tech']} ELSE 0 END"
        )

    for kw in keywords["location"]:
        safe_kw = _sanitize_keyword(kw)
        if not safe_kw:
            continue
        score_parts.append(
            f"CASE WHEN LOWER(location) LIKE '%{safe_kw}%' "
            f"THEN {FIELD_WEIGHTS['location']} ELSE 0 END"
        )

    if not score_parts:
        return "SELECT NULL::int AS id, NULL::int AS rank WHERE false"

    score_expr = " + ".join(score_parts)

    return f"""
        SELECT
            id,
            ROW_NUMBER() OVER (ORDER BY weighted_score DESC) AS rank
        FROM (
            SELECT id, ({score_expr}) AS weighted_score
            FROM salary_posts
            WHERE ({score_expr}) > 0
        ) scored
    """
```


## `backend/app/rag/reranker.py`

```python
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
import json

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def rerank_results(query: str, posts: list[dict], top_k: int = 3) -> list[dict]:
    """
    Re-ranks search results by true relevance to the query.
    GPT reads all candidates and returns the most relevant order.
    """
    if not posts:
        return []

    if len(posts) <= 2:
        return posts[:top_k]

    # Build structured posts text
    posts_text = "\n".join([
        f"Post {i+1}: Role: {p['role']} | "
        f"Salary: {p['salary']}₪ | "
        f"Experience: {p['years_experience']} years | "
        f"Location: {p['location']}"
        for i, p in enumerate(posts)
    ])

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You rank salary posts by relevance to a question. Return ONLY a JSON array of integers like [2, 1, 3]. No explanation, no markdown, just the array."
                },
                {
                    "role": "user",
                    "content": f"Question: {query}\n\n{posts_text}\n\nReturn the ranking array:"
                }
            ],
            temperature=0,
            max_tokens=50,
        )

        raw = response.choices[0].message.content.strip()
        ranking = json.loads(raw)

        if not isinstance(ranking, list) or len(ranking) == 0:
            raise ValueError(f"Invalid ranking: {raw}")

        # Deduplicate and validate
        reranked = []
        seen_ids = set()
        for i in ranking:
            if 1 <= i <= len(posts):
                post = posts[i-1]
                if post["id"] not in seen_ids:
                    seen_ids.add(post["id"])
                    reranked.append(post)

        if not reranked:
            raise ValueError("Empty after dedup")

        logger.info(f"Reranking successful: {[p['role'] for p in reranked[:top_k]]}")
        return reranked[:top_k]

    except json.JSONDecodeError as e:
        logger.warning(f"Reranker invalid JSON: '{raw}' | {e} | falling back")
        return posts[:top_k]

    except Exception as e:
        logger.warning(f"Reranking failed: {e} | falling back")
        return posts[:top_k]
```


## `backend/app/rag/generator.py`

```python
import asyncio
from openai import AsyncOpenAI, APIConnectionError, RateLimitError
from app.core.config import settings
from app.core.exceptions import GenerationError, RetrievalError
from app.core.logging import get_logger
from app.core.query_logger import QueryTracker
from app.rag.retriever import search_similar_posts
from app.rag.reranker import rerank_results

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """You are an expert on the Israeli tech job market.
Answer salary questions based only on the real community data provided.

Rules:
- Only use the data provided. Never invent numbers.
- If there is not enough data — say so explicitly.
- Give a salary range, not a single number, when possible.
- Answer in Hebrew, clearly and directly.
- At the end, state how many posts you used."""


async def answer_salary_query(query: str) -> dict:
    if not query or not query.strip():
        raise ValueError("Empty query")

    tracker = QueryTracker(query)
    estimated_cost = 0.0

    logger.info(f"Query received: '{query}'")

    # Stage 1 — Retrieve
    try:
        with tracker.track_stage("retrieval"):
            candidates = await search_similar_posts(query, limit=10)

        tracker.posts_retrieved = len(candidates)
        tracker.retrieved_post_ids = [p["id"] for p in candidates]

    except Exception as e:
        logger.error(f"Retrieval error: {e}")
        tracker.success = False
        tracker.error_message = str(e)
        tracker.save()
        raise RetrievalError("Failed to retrieve relevant data")

    if not candidates:
        logger.warning(f"No results for: '{query}'")
        tracker.save()
        return {
            "answer": "לא נמצאו נתונים רלוונטיים לשאלה שלך.",
            "sources": [],
            "posts_used": 0
        }

    # Stage 2 — Rerank
    try:
        with tracker.track_stage("reranking"):
            relevant_posts = await rerank_results(query, candidates, top_k=3)
    except Exception as e:
        logger.warning(f"Reranking failed, falling back: {e}")
        relevant_posts = candidates[:3]

    tracker.posts_after_rerank = len(relevant_posts)

    # Stage 3 — Generate
    try:
        with tracker.track_stage("generation"):
            context = _build_context(relevant_posts)

            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Data:\n{context}\n\nQuestion: {query}"}
                ],
                temperature=0.3,
            )

        answer = response.choices[0].message.content
        usage = response.usage
        estimated_cost = tracker.add_tokens(
            usage.prompt_tokens,
            usage.completion_tokens
        )

    except RateLimitError:
        tracker.success = False
        tracker.error_message = "RateLimitError"
        tracker.save(estimated_cost)
        raise GenerationError("Server overloaded, please try again")

    except APIConnectionError:
        tracker.success = False
        tracker.error_message = "APIConnectionError"
        tracker.save(estimated_cost)
        raise GenerationError("AI server connection error")

    tracker.save(estimated_cost)

    return {
        "answer": answer,
        "sources": relevant_posts,
        "posts_used": len(relevant_posts)
    }


def _build_context(posts: list[dict]) -> str:
    lines = []
    for i, post in enumerate(posts, 1):
        lines.append(
            f"Post {i}:\n"
            f"Role: {post['role']} | "
            f"Experience: {post['years_experience']} years | "
            f"Salary: {post['salary']}₪ | "
            f"Location: {post['location']}\n"
            f"Quote: {post['raw_text']}\n"
        )
    return "\n".join(lines)
```


## `backend/app/rag/evaluator.py`

```python
import math
from app.rag.retriever import search_similar_posts
from app.core.logging import get_logger

logger = get_logger(__name__)


def hit_rate_at_k(results: list[dict], relevant_ids: list[int], k: int) -> float:
    """
    האם לפחות אחת מה-relevant_ids הופיעה בtop-k תוצאות?
    מחזיר 1.0 או 0.0
    """
    top_k_ids = [r["id"] for r in results[:k]]
    return 1.0 if any(rid in top_k_ids for rid in relevant_ids) else 0.0


def reciprocal_rank(results: list[dict], relevant_ids: list[int]) -> float:
    """
    1/rank של התוצאה הרלוונטית הראשונה.
    אם לא נמצאה — 0.
    """
    for i, result in enumerate(results, 1):
        if result["id"] in relevant_ids:
            return 1.0 / i
    return 0.0


def ndcg_at_k(results: list[dict], relevant_ids: list[int], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain.
    מתחשב בדירוג של כל התוצאות הרלוונטיות.
    """
    def dcg(hits: list[int]) -> float:
        return sum(
            hit / math.log2(i + 2)
            for i, hit in enumerate(hits[:k])
        )

    # DCG של התוצאות שלנו
    hits = [1 if r["id"] in relevant_ids else 0 for r in results[:k]]
    actual_dcg = dcg(hits)

    # DCG אידיאלי — כל הרלוונטיים ראשונים
    ideal_hits = sorted(hits, reverse=True)
    ideal_dcg = dcg(ideal_hits)

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg


def evaluate_retrieval(test_cases: list[dict], k: int = 3) -> dict:
    """
    מריץ evaluation על רשימת test cases.

    כל test case:
    {
        "query": "כמה מרוויח DevOps?",
        "relevant_ids": [2]  ← IDs של פוסטים רלוונטיים
    }
    """
    hit_rates = []
    mrr_scores = []
    ndcg_scores = []

    logger.info(f"מריץ evaluation על {len(test_cases)} שאלות...")

    for i, case in enumerate(test_cases, 1):
        query = case["query"]
        relevant_ids = case["relevant_ids"]

        results = search_similar_posts(query, limit=k)

        hr = hit_rate_at_k(results, relevant_ids, k)
        rr = reciprocal_rank(results, relevant_ids)
        ndcg = ndcg_at_k(results, relevant_ids, k)

        hit_rates.append(hr)
        mrr_scores.append(rr)
        ndcg_scores.append(ndcg)

        status = "✓" if hr == 1.0 else "✗"
        logger.info(
            f"  [{i}] {status} '{query[:40]}' | "
            f"HR={hr:.1f} MRR={rr:.2f} NDCG={ndcg:.2f}"
        )

    metrics = {
        "hit_rate_at_k": round(sum(hit_rates) / len(hit_rates), 3),
        "mrr": round(sum(mrr_scores) / len(mrr_scores), 3),
        "ndcg_at_k": round(sum(ndcg_scores) / len(ndcg_scores), 3),
        "k": k,
        "total_queries": len(test_cases),
    }

    logger.info(f"\n{'='*50}")
    logger.info(f"Hit Rate@{k}: {metrics['hit_rate_at_k']}")
    logger.info(f"MRR:         {metrics['mrr']}")
    logger.info(f"NDCG@{k}:    {metrics['ndcg_at_k']}")
    logger.info(f"{'='*50}")

    return metrics
```


## `backend/app/rag/qa_generator.py`

```python
import asyncio
import json
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.logging import get_logger
from app.db.database import SessionLocal
from app.db.models import SalaryPost

logger = get_logger(__name__)
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def generate_question_for_post(post: dict) -> str | None:
    """
    Given a salary post, generate a natural Hebrew question
    that this post would answer.
    """
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are helping build a salary search evaluation dataset.
Given a salary post from an Israeli tech community, generate ONE natural Hebrew question
that someone would ask, where this post would be a relevant answer.

Rules:
- Question must be in Hebrew
- Must sound like a real person asking
- Should NOT copy exact words from the post
- Should be about salary for this role/experience level
- Return ONLY the question, nothing else"""
            },
            {
                "role": "user",
                "content": f"""Post:
Role: {post['role']}
Experience: {post['years_experience']} years
Salary: {post['salary']}
Location: {post['location']}
Text: {post['raw_text']}"""
            }
        ],
        temperature=0.7,
        max_tokens=100,
    )

    question = response.choices[0].message.content.strip()

    if not question or len(question) < 10:
        return None

    return question


async def generate_test_cases(limit: int = 50) -> list[dict]:
    """
    Generate synthetic test cases from existing posts in the DB.
    Each post becomes one test case with a generated question.
    """
    db = SessionLocal()
    try:
        posts = db.query(SalaryPost).filter(
            SalaryPost.role.isnot(None),
            SalaryPost.salary.isnot(None),
            SalaryPost.years_experience.isnot(None),
        ).limit(limit).all()

        logger.info(f"Generating questions for {len(posts)} posts...")

        test_cases = []
        for i, post in enumerate(posts, 1):
            post_dict = {
                "id": post.id,
                "role": post.role,
                "years_experience": post.years_experience,
                "salary": post.salary,
                "location": post.location,
                "raw_text": post.raw_text,
            }

            question = await generate_question_for_post(post_dict)

            if question:
                test_cases.append({
                    "query": question,
                    "relevant_ids": [post.id],
                    "source_post": post_dict,
                })
                logger.info(f"[{i}/{len(posts)}] {post.role} → {question[:50]}...")
            else:
                logger.warning(f"[{i}/{len(posts)}] Failed for post {post.id}")

        return test_cases

    finally:
        db.close()


async def main():
    test_cases = await generate_test_cases(limit=50)

    output_path = "app/generated_test_cases.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(test_cases, f, ensure_ascii=False, indent=2)

    print(f"\n✓ Generated {len(test_cases)} test cases")
    print(f"✓ Saved to {output_path}")
    print("\nSample:")
    for tc in test_cases[:3]:
        print(f"  Q: {tc['query']}")
        print(f"  A: post_id={tc['relevant_ids'][0]} ({tc['source_post']['role']})")
        print()


if __name__ == "__main__":
    asyncio.run(main())
```


## `backend/app/rag/test_cases.py`

```python
"""
Test cases לevaluation.

relevant_ids = IDs של פוסטים שצריכים להופיע בתוצאות.
אלה ה-IDs מהseed_data שלנו — בדוק ב-DB אם שונים.
"""

TEST_CASES = [
    {
        "query": "כמה מרוויח מפתח פרונטאנד בתל אביב?",
        "relevant_ids": [1],  # Frontend Developer
    },
    {
        "query": "שכר DevOps עם ניסיון בחברה גדולה",
        "relevant_ids": [2],  # DevOps
    },
    {
        "query": "כמה מקבל data scientist מתחיל?",
        "relevant_ids": [4],  # Data Scientist
    },
    {
        "query": "מה השכר של team lead בפינטק?",
        "relevant_ids": [3],  # Team Lead
    },
    {
        "query": "Python backend developer כמה מרוויח?",
        "relevant_ids": [5],  # Backend Developer
    },
]
```


## `backend/app/ablation_study.py`

```python
import asyncio
import sys
sys.path.append(".")

from app.rag.evaluator import hit_rate_at_k, reciprocal_rank, ndcg_at_k
from app.rag.embeddings import get_embedding
from app.rag.query_parser import expand_query
from app.rag.reranker import rerank_results
from app.db.database import SessionLocal
from sqlalchemy import text
import json

# Load generated test cases instead of manual ones
with open("app/generated_test_cases.json", "r", encoding="utf-8") as f:
    TEST_CASES = json.load(f)

K = 3
THRESHOLD = 0.25
RRF_K = 60


# ── Version 1: Semantic only ──────────────────────────────────────────────────

async def search_semantic_only(query: str, limit: int) -> list[dict]:
    embedding = await get_embedding(query)
    db = SessionLocal()
    try:
        results = db.execute(text("""
            SELECT id, role, salary, years_experience, location,
                   1 - (embedding <=> CAST(:emb AS vector)) AS similarity
            FROM salary_posts
            WHERE 1 - (embedding <=> CAST(:emb AS vector)) > :threshold
            ORDER BY embedding <=> CAST(:emb AS vector)
            LIMIT :limit
        """), {"emb": str(embedding), "threshold": THRESHOLD, "limit": limit}).fetchall()

        return [{"id": r.id, "role": r.role, "salary": r.salary,
                 "years_experience": r.years_experience, "location": r.location,
                 "similarity": round(r.similarity, 3)} for r in results]
    finally:
        db.close()


# ── Version 2: Hybrid (no expansion) ─────────────────────────────────────────

async def search_hybrid_no_expansion(query: str, limit: int) -> list[dict]:
    embedding = await get_embedding(query)

    # Simple keyword: search the query directly on role/location
    db = SessionLocal()
    try:
        results = db.execute(text(f"""
            WITH semantic AS (
                SELECT id,
                       1 - (embedding <=> CAST(:emb AS vector)) AS similarity,
                       ROW_NUMBER() OVER (ORDER BY embedding <=> CAST(:emb AS vector)) AS rank
                FROM salary_posts
                WHERE 1 - (embedding <=> CAST(:emb AS vector)) > :threshold
            ),
            keyword AS (
                SELECT id,
                       ROW_NUMBER() OVER (ORDER BY match_score DESC) AS rank
                FROM (
                    SELECT id,
                           CASE WHEN LOWER(role) LIKE :pattern THEN 3 ELSE 0 END +
                           CASE WHEN LOWER(location) LIKE :pattern THEN 1 ELSE 0 END AS match_score
                    FROM salary_posts
                    WHERE LOWER(role) LIKE :pattern OR LOWER(location) LIKE :pattern
                ) scored WHERE match_score > 0
            ),
            rrf AS (
                SELECT COALESCE(s.id, k.id) AS id,
                       COALESCE(1.0/(:rrf_k+s.rank),0) + COALESCE(1.0/(:rrf_k+k.rank),0) AS rrf_score,
                       COALESCE(s.similarity,0) AS similarity
                FROM semantic s FULL OUTER JOIN keyword k ON s.id=k.id
            )
            SELECT p.id, p.role, p.salary, p.years_experience, p.location,
                   r.similarity, r.rrf_score
            FROM rrf r JOIN salary_posts p ON p.id=r.id
            ORDER BY r.rrf_score DESC LIMIT :limit
        """), {
            "emb": str(embedding),
            "threshold": THRESHOLD,
            "rrf_k": RRF_K,
            "pattern": f"%{query.lower()[:20]}%",
            "limit": limit
        }).fetchall()

        return [{"id": r.id, "role": r.role, "salary": r.salary,
                 "years_experience": r.years_experience, "location": r.location,
                 "similarity": round(r.similarity, 3)} for r in results]
    finally:
        db.close()


# ── Version 3: Hybrid + Query Expansion (no reranking) ───────────────────────

async def search_hybrid_with_expansion(query: str, limit: int) -> list[dict]:
    from app.rag.retriever import search_similar_posts
    return await search_similar_posts(query, limit=limit)


# ── Version 4: Full pipeline ──────────────────────────────────────────────────

async def search_full_pipeline(query: str, limit: int) -> list[dict]:
    from app.rag.retriever import search_similar_posts
    candidates = await search_similar_posts(query, limit=limit)
    return await rerank_results(query, candidates, top_k=K)


# ── Evaluation runner ─────────────────────────────────────────────────────────

async def evaluate_version(name: str, search_fn, limit: int = 10) -> dict:
    print(f"\n{'─'*50}")
    print(f"Version: {name}")
    print('─'*50)

    hit_rates, mrr_scores, ndcg_scores = [], [], []

    for case in TEST_CASES:
        results = await search_fn(case["query"], limit)
        hr   = hit_rate_at_k(results, case["relevant_ids"], K)
        rr   = reciprocal_rank(results, case["relevant_ids"])
        ndcg = ndcg_at_k(results, case["relevant_ids"], K)

        hit_rates.append(hr)
        mrr_scores.append(rr)
        ndcg_scores.append(ndcg)

        status = "✓" if hr == 1.0 else "✗"
        print(f"  {status} '{case['query'][:40]}' | HR={hr:.1f} MRR={rr:.2f} NDCG={ndcg:.2f}")

    metrics = {
        "name": name,
        "hit_rate": round(sum(hit_rates) / len(hit_rates), 3),
        "mrr":      round(sum(mrr_scores) / len(mrr_scores), 3),
        "ndcg":     round(sum(ndcg_scores) / len(ndcg_scores), 3),
    }

    print(f"\n  Hit Rate@{K}: {metrics['hit_rate']}")
    print(f"  MRR:         {metrics['mrr']}")
    print(f"  NDCG@{K}:    {metrics['ndcg']}")

    return metrics


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print("\n🔬 Ablation Study — Salary Intel RAG Pipeline")
    print("=" * 50)

    versions = [
        ("1. Semantic Only",                    search_semantic_only),
        ("2. Hybrid (no expansion)",             search_hybrid_no_expansion),
        ("3. Hybrid + Query Expansion",          search_hybrid_with_expansion),
        ("4. Full Pipeline (+ Reranking)",       search_full_pipeline),
    ]

    all_metrics = []
    for name, fn in versions:
        metrics = await evaluate_version(name, fn)
        all_metrics.append(metrics)

    # Summary table
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Version':<40} {'Hit Rate':>10} {'MRR':>8} {'NDCG':>8}")
    print(f"{'─'*60}")
    for m in all_metrics:
        print(f"{m['name']:<40} {m['hit_rate']:>10} {m['mrr']:>8} {m['ndcg']:>8}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
```


## `backend/app/ingestion/extractor.py`

```python
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
```


## `backend/app/ingestion/ingestor.py`

```python
import asyncio
from sqlalchemy.orm import Session
from app.db.models import SalaryPost
from app.rag.embeddings import get_embedding
from app.db.database import SessionLocal
from app.ingestion.extractor import extract_salary_data
from app.core.logging import get_logger
from app.core.exceptions import SalaryIntelError
from datetime import datetime

logger = get_logger(__name__)


async def ingest_post(
    raw_text: str,
    role: str | None = None,
    years_experience: float | None = None,
    salary: float | None = None,
    company_stage: str | None = None,
    location: str | None = None,
    source: str = "manual",
    post_date: datetime | None = None,
    auto_extract: bool = False,
) -> SalaryPost:
    if not raw_text or not raw_text.strip():
        raise ValueError("Empty text — cannot ingest")

    if auto_extract:
        logger.info("Auto-extracting metadata...")
        extracted = await extract_salary_data(raw_text)

        if not extracted["is_salary_post"]:
            logger.warning("Post is not about salary — skipping")
            raise ValueError("Post is not about salary")

        role = role or extracted["role"]
        salary = salary or extracted["salary"]
        years_experience = years_experience or extracted["years_experience"]
        company_stage = company_stage or extracted["company_stage"]
        location = location or extracted["location"]

    logger.info(f"Ingesting: {role} | {salary}₪")

    try:
        embedding_text = _build_embedding_text(
            raw_text, role, years_experience, salary, location
        )
        embedding = await get_embedding(embedding_text)
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise SalaryIntelError("Failed to process post")

    db: Session = SessionLocal()
    try:
        post = SalaryPost(
            raw_text=raw_text,
            role=role,
            years_experience=years_experience,
            salary=salary,
            company_stage=company_stage,
            location=location,
            embedding=embedding,
            source=source,
            post_date=post_date or datetime.utcnow(),
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        logger.info(f"Saved | id={post.id}")
        return post

    except Exception as e:
        db.rollback()
        logger.error(f"DB error: {e}")
        raise SalaryIntelError("Error saving post")
    finally:
        db.close()


def _build_embedding_text(
    raw_text: str,
    role: str | None,
    years_experience: float | None,
    salary: float | None,
    location: str | None,
) -> str:
    parts = [raw_text]
    if role:
        parts.append(f"Role: {role}")
    if years_experience:
        parts.append(f"Experience: {years_experience} years")
    if salary:
        parts.append(f"Salary: {salary}")
    if location:
        parts.append(f"Location: {location}")
    return " | ".join(parts)
```


## `backend/app/ingestion/bulk_ingestor.py`

```python
from app.ingestion.ingestor import ingest_post
from app.core.logging import get_logger

logger = get_logger(__name__)


async def bulk_ingest(posts: list[str], source: str = "facebook") -> dict:
    """
    Ingests a list of raw posts with automatic metadata extraction.
    """
    results = {
        "success": 0,
        "skipped": 0,
        "failed": 0,
        "total": len(posts),
    }

    for i, raw_text in enumerate(posts, 1):
        logger.info(f"[{i}/{len(posts)}] Processing post...")

        try:
            await ingest_post(
                raw_text=raw_text,
                source=source,
                auto_extract=True,
            )
            results["success"] += 1

        except ValueError as e:
            logger.info(f"Skipped: {e}")
            results["skipped"] += 1

        except Exception as e:
            logger.error(f"Failed: {e}")
            results["failed"] += 1

    logger.info(
        f"\nSummary: {results['success']} succeeded | "
        f"{results['skipped']} skipped | "
        f"{results['failed']} failed"
    )

    return results
```


## `backend/app/ingestion/data_generator.py`

```python
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
```


## `backend/app/ingestion/sample_data.py`

```python
SAMPLE_POSTS = [
    {
        "raw_text": "היי כולם, מפתח React עם 4 שנות ניסיון. עובד בסטארטאפ סדרה B בתל אביב. קיבלתי הצעה של 28K. נשמע הגיוני?",
        "role": "Frontend Developer",
        "years_experience": 4,
        "salary": 28000,
        "company_stage": "Series B",
        "location": "תל אביב",
        "source": "facebook",
    },
    {
        "raw_text": "עדכון שכר לקהילה: DevOps עם 6 שנים, חברה פיננסית גדולה, מרכז. 42K + בונוס שנתי. שוק מאוד חזק כרגע.",
        "role": "DevOps",
        "years_experience": 6,
        "salary": 42000,
        "company_stage": "Enterprise",
        "location": "מרכז",
        "source": "facebook",
    },
    {
        "raw_text": "Team Lead בחברת פינטק, 8 שנות ניסיון, 3 שנים ניהול. מקבל 55K כולל רכב. תל אביב.",
        "role": "Team Lead",
        "years_experience": 8,
        "salary": 55000,
        "company_stage": "Fintech",
        "location": "תל אביב",
        "source": "facebook",
    },
    {
        "raw_text": "Data Scientist ג׳וניור, שנה וחצי ניסיון, חברת SaaS. מציעים לי 22K. זה בסדר לג׳וניור?",
        "role": "Data Scientist",
        "years_experience": 1.5,
        "salary": 22000,
        "company_stage": "SaaS",
        "location": "תל אביב",
        "source": "facebook",
    },
    {
        "raw_text": "Backend Python, 5 שנים, חברת אינטרנט בינונית, רמת גן. 34K. עוברים ל-FastAPI, מאוד מרוצה מהסביבה.",
        "role": "Backend Developer",
        "years_experience": 5,
        "salary": 34000,
        "company_stage": "Growth",
        "location": "רמת גן",
        "source": "facebook",
    },
]
```


## `backend/seed_data.py`

```python
import sys
sys.path.append(".")

from app.ingestion.ingestor import ingest_post
from app.ingestion.sample_data import SAMPLE_POSTS
from app.db.database import SessionLocal
from app.db.models import SalaryPost

def seed():
    db = SessionLocal()
    try:
        count = db.query(SalaryPost).count()
        if count > 0:
            print(f"⚠️  המסד כבר מכיל {count} פוסטים — מדלג על seed")
            return
    finally:
        db.close()

    print(f"מכניס {len(SAMPLE_POSTS)} פוסטים...")
    for i, post in enumerate(SAMPLE_POSTS):
        result = ingest_post(**post)
        print(f"✓ [{i+1}] {result.role} — {result.salary}₪  (id: {result.id})")

    print("\n✓ הכל נשמר במסד")

if __name__ == "__main__":
    seed()
```


## `frontend/package.json`

```json
{
  "name": "frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint"
  },
  "dependencies": {
    "next": "16.2.6",
    "react": "19.2.4",
    "react-dom": "19.2.4"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4",
    "@types/node": "^20",
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "eslint": "^9",
    "eslint-config-next": "16.2.6",
    "tailwindcss": "^4",
    "typescript": "^5"
  }
}
```


## `frontend/lib/api.ts`

```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY || "my-super-secret-key-2024";

export interface Source {
  id: number;
  role: string;
  salary: number;
  years_experience: number;
  location: string;
  raw_text: string;
  similarity: number;
}

export interface QueryResponse {
  answer: string;
  posts_used: number;
  sources: Source[];
}

export async function querySalary(query: string): Promise<QueryResponse> {
  const response = await fetch(`${API_URL}/api/v1/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY,
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Server error");
  }

  return response.json();
}
```


## `frontend/app/api/query/route.ts`

```typescript
// No API_KEY here — the browser never sees it
export interface Source {
    id: number;
    role: string;
    salary: number;
    years_experience: number;
    location: string;
    raw_text: string;
    similarity: number;
  }
  
  export interface QueryResponse {
    answer: string;
    posts_used: number;
    sources: Source[];
  }
  
  export async function querySalary(query: string): Promise<QueryResponse> {
    // Calls our own Next.js server, not the backend directly
    const response = await fetch("/api/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query }),
    });
  
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Server error");
    }
  
    return response.json();
  }
```


## `frontend/app/page.tsx`

```tsx
"use client";

import { useState } from "react";
import { querySalary, QueryResponse } from "@/lib/api";

export default function Home() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await querySalary(query);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unexpected error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main dir="rtl" style={{ minHeight: "100vh", background: "linear-gradient(160deg, #f0f4ff 0%, #e8eeff 40%, #f0f9ff 100%)", fontFamily: "sans-serif" }}>

      {/* Glow blobs */}
      <div style={{ position: "fixed", top: -200, right: -200, width: 600, height: 600, borderRadius: "50%", background: "radial-gradient(circle, rgba(99,102,241,0.12), transparent)", pointerEvents: "none" }} />
      <div style={{ position: "fixed", bottom: -200, left: -200, width: 500, height: 500, borderRadius: "50%", background: "radial-gradient(circle, rgba(59,130,246,0.1), transparent)", pointerEvents: "none" }} />

      {/* Header */}
      <header style={{ borderBottom: "1px solid rgba(99,102,241,0.1)", background: "rgba(255,255,255,0.7)", backdropFilter: "blur(12px)", position: "sticky", top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: 760, margin: "0 auto", padding: "14px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 28, height: 28, borderRadius: 8, background: "linear-gradient(135deg, #6366f1, #3b82f6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14 }}>🔍</div>
            <span style={{ fontWeight: 700, fontSize: 16, color: "#1e1b4b" }}>Salary Intel</span>
          </div>
          <span style={{ fontSize: 12, color: "#6366f1", background: "rgba(99,102,241,0.08)", border: "1px solid rgba(99,102,241,0.15)", borderRadius: 20, padding: "4px 12px" }}>
            🇮🇱 שוק ההייטק הישראלי
          </span>
        </div>
      </header>

      {/* Hero */}
      <div style={{ maxWidth: 760, margin: "0 auto", padding: "60px 24px 32px", textAlign: "center" }}>

        {/* Badge */}
        <div style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "white", border: "1px solid rgba(99,102,241,0.2)", borderRadius: 24, padding: "6px 16px", fontSize: 13, color: "#6366f1", marginBottom: 28, boxShadow: "0 2px 12px rgba(99,102,241,0.08)" }}>
          <span style={{ width: 8, height: 8, background: "#4ade80", borderRadius: "50%", display: "inline-block", animation: "pulse 2s infinite" }} />
          מבוסס על קבוצת הפייסבוק ״משכורות בהייטקס״
          </div>

        {/* Headline */}
        <h1 style={{ fontSize: 52, fontWeight: 800, lineHeight: 1.15, color: "#1e1b4b", marginBottom: 16 }}>
          כמה אתה{" "}
          <span style={{ background: "linear-gradient(90deg, #6366f1 0%, #3b82f6 100%)", backgroundClip: "text", WebkitBackgroundClip: "text", color: "transparent", WebkitTextFillColor: "transparent", display: "inline-block" }}>
            שווה?
          </span>
        </h1>

        <p style={{ fontSize: 17, color: "#64748b", marginBottom: 36, lineHeight: 1.6 }}>
          תובנות שכר חכמות מבוססות AI — ממאות דיונים אמיתיים בקהילת ההייטק הישראלית
        </p>

        {/* Search box */}
        <form onSubmit={handleSubmit}>
          <div style={{ display: "flex", gap: 8, background: "white", border: "1.5px solid rgba(99,102,241,0.2)", borderRadius: 18, padding: 8, boxShadow: "0 8px 32px rgba(99,102,241,0.1)" }}>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="כמה מרוויח מפתח React עם 4 שנות ניסיון בתל אביב?"
              disabled={loading}
              style={{ flex: 1, background: "transparent", border: "none", outline: "none", padding: "12px 16px", fontSize: 15, color: "#1e1b4b", textAlign: "right", direction: "rtl" }}
            />
            <button
              type="submit"
              disabled={loading || !query.trim()}
              style={{ padding: "12px 24px", borderRadius: 12, border: "none", cursor: loading || !query.trim() ? "not-allowed" : "pointer", background: "linear-gradient(135deg, #6366f1, #3b82f6)", color: "white", fontWeight: 600, fontSize: 15, opacity: loading || !query.trim() ? 0.6 : 1, transition: "all 0.2s", display: "flex", alignItems: "center", gap: 8 }}
            >
              {loading ? (
                <>
                  <span style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTop: "2px solid white", borderRadius: "50%", display: "inline-block", animation: "spin 0.8s linear infinite" }} />
                  מחפש
                </>
              ) : "חפש →"}
            </button>
          </div>
        </form>

        {/* Example chips */}
        <div style={{ display: "flex", gap: 8, marginTop: 16, flexWrap: "wrap", justifyContent: "center" }}>
          {["כמה מרוויח DevOps בכיר?", "שכר data scientist מתחיל", "מה מקבל team lead בפינטק?"].map((ex) => (
            <button
              key={ex}
              onClick={() => setQuery(ex)}
              style={{ fontSize: 13, color: "#6366f1", background: "white", border: "1px solid rgba(99,102,241,0.15)", borderRadius: 20, padding: "6px 14px", cursor: "pointer", transition: "all 0.2s", boxShadow: "0 1px 4px rgba(0,0,0,0.04)" }}
            >
              {ex}
            </button>
          ))}
        </div>
      </div>

      {/* Results */}
      <div style={{ maxWidth: 760, margin: "0 auto", padding: "0 24px 80px" }}>

        {error && (
          <div style={{ background: "#fef2f2", border: "1px solid #fecaca", borderRadius: 16, padding: 16, color: "#dc2626", fontSize: 14 }}>
            {error}
          </div>
        )}

        {loading && (
          <div style={{ textAlign: "center", padding: "64px 0" }}>
            <div style={{ width: 48, height: 48, borderRadius: "50%", background: "conic-gradient(from 0deg, #6366f1, #3b82f6, #e0e7ff)", animation: "spin 1s linear infinite", margin: "0 auto 16px" }} />
            <p style={{ color: "#94a3b8", fontSize: 14 }}>מחפש בנתוני הקהילה...</p>
          </div>
        )}

        {result && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

            {/* Answer card */}
            <div style={{ background: "linear-gradient(135deg, #ffffff 0%, #f5f3ff 100%)", border: "1.5px solid rgba(99,102,241,0.15)", borderRadius: 20, padding: 28, boxShadow: "0 8px 32px rgba(99,102,241,0.08)" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg, #6366f1, #3b82f6)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 18 }}>💡</div>
                  <span style={{ fontWeight: 700, fontSize: 16, color: "#1e1b4b" }}>תשובה</span>
                </div>
                <span style={{ fontSize: 12, color: "#94a3b8", background: "#f8fafc", border: "1px solid #e2e8f0", borderRadius: 20, padding: "4px 12px" }}>
                  מבוסס על {result.posts_used} פוסטים
                </span>
              </div>
              <p style={{ color: "#334155", lineHeight: 1.8, fontSize: 15, whiteSpace: "pre-wrap" }}>
                {result.answer}
              </p>
            </div>

            {/* Sources */}
            {result.sources.length > 0 && (
              <div>
                <p style={{ color: "#94a3b8", fontSize: 13, marginBottom: 10, paddingRight: 4 }}>מקורות</p>
                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {result.sources.map((source) => (
                    <div
                      key={source.id}
                      style={{ background: "white", border: "1px solid #e8eeff", borderRadius: 16, padding: 18, boxShadow: "0 2px 8px rgba(0,0,0,0.04)", transition: "all 0.2s" }}
                    >
                      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8, flexWrap: "wrap" }}>
                        <span style={{ fontWeight: 600, fontSize: 14, color: "#1e1b4b" }}>{source.role}</span>
                        {source.salary && (
                          <span style={{ fontWeight: 700, fontSize: 13, background: "linear-gradient(135deg, #ede9fe, #dbeafe)", color: "#4f46e5", borderRadius: 8, padding: "3px 10px" }}>
                            ₪{source.salary.toLocaleString()}
                          </span>
                        )}
                        {source.years_experience && (
                          <span style={{ fontSize: 12, color: "#94a3b8" }}>{source.years_experience} שנים</span>
                        )}
                        {source.location && (
                          <span style={{ fontSize: 12, color: "#94a3b8" }}>📍 {source.location}</span>
                        )}
                        <span style={{ fontSize: 11, color: "#cbd5e1", marginRight: "auto" }}>
                          {Math.round(source.similarity * 100)}% התאמה
                        </span>
                      </div>
                      <p style={{ color: "#64748b", fontSize: 13, lineHeight: 1.6 }}>{source.raw_text}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
      `}</style>
    </main>
  );
}
```


## `frontend/app/layout.tsx`

```tsx
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Create Next App",
  description: "Generated by create next app",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
```
