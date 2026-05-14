from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.rag.generator import answer_salary_query
from app.ingestion.ingestor import ingest_post
from app.core.exceptions import SalaryIntelError
from app.core.logging import get_logger

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
def query_salary(request: QueryRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="שאלה ריקה")

    try:
        result = answer_salary_query(request.query)
        return QueryResponse(**result)

    except SalaryIntelError as e:
        # שגיאות צפויות — הודעה ברורה למשתמש
        logger.warning(f"SalaryIntelError: {e}")
        raise HTTPException(status_code=503, detail=str(e))

    except Exception as e:
        # שגיאות לא צפויות — לא חושפים פרטים טכניים
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="שגיאה פנימית")


@router.post("/ingest")
def ingest_new_post(request: IngestRequest):
    try:
        post = ingest_post(**request.model_dump())
        return {"id": post.id, "message": "נשמר בהצלחה"}

    except SalaryIntelError as e:
        logger.warning(f"Ingest error: {e}")
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error(f"Unexpected ingest error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="שגיאה בשמירת הפוסט")


@router.get("/stats")
def get_stats():
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