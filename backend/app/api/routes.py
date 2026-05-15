from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from app.rag.generator import answer_salary_query
from app.ingestion.ingestor import ingest_post
from app.core.exceptions import SalaryIntelError
from app.core.logging import get_logger
from app.core.rate_limiter import limiter

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
@limiter.limit("3/minute")  # ← מקסימום 10 שאלות בדקה לכל IP
def query_salary(request: Request, body: QueryRequest):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="שאלה ריקה")

    try:
        result = answer_salary_query(body.query)
        return QueryResponse(**result)

    except SalaryIntelError as e:
        logger.warning(f"SalaryIntelError: {e}")
        raise HTTPException(status_code=503, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="שגיאה פנימית")


@router.post("/ingest")
@limiter.limit("5/minute")  # ← ingestion מוגבל יותר
def ingest_new_post(request: Request, body: IngestRequest):
    try:
        post = ingest_post(**body.model_dump())
        return {"id": post.id, "message": "נשמר בהצלחה"}

    except SalaryIntelError as e:
        logger.warning(f"Ingest error: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected ingest error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="שגיאה בשמירת הפוסט")


@router.get("/stats")
@limiter.limit("30/minute")
def get_stats(request: Request):
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
        raise HTTPException(status_code=500, detail="שגיאה בטעינת סטטיסטיקות")