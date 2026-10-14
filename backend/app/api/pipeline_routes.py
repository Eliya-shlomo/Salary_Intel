from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.rate_limiter import limiter
from app.core.security import verify_api_key
from app.db.database import get_db
from app.db.models import SalaryPost
from app.ingestion.orchestrator import ingest_pipeline

logger = get_logger(__name__)
router = APIRouter()

STATUS_CODE_BY_OUTCOME = {
    "approved": 201,
    "pending": 202,
    "duplicate": 409,
    "rejected": 422,
}


class PostRequest(BaseModel):
    raw_text: str = Field(min_length=1, max_length=5000)
    source: str = Field(default="manual", max_length=100)


@router.post("/posts")
@limiter.limit("5/minute")
async def submit_post(
    request: Request,
    body: PostRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    try:
        outcome = await ingest_pipeline(db, body.raw_text, source=body.source)
        db.commit()
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Pipeline error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing post")

    return JSONResponse(
        status_code=STATUS_CODE_BY_OUTCOME[outcome.status],
        content=outcome.model_dump(),
    )


@router.get("/review/pending")
@limiter.limit("30/minute")
def list_pending(
    request: Request,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    posts = (
        db.query(SalaryPost)
        .filter(SalaryPost.review_status == "pending")
        .order_by(SalaryPost.id.desc())
        .limit(50)
        .all()
    )
    return [
        {
            "id": p.id,
            "raw_text": p.raw_text,
            "role": p.role,
            "salary_min": p.salary_min,
            "salary_max": p.salary_max,
            "pay_basis": p.pay_basis,
            "has_equity": p.has_equity,
            "evidence": p.evidence,
        }
        for p in posts
    ]


def _decide(db: Session, post_id: int, new_status: str) -> dict:
    post = db.get(SalaryPost, post_id)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.review_status == new_status:
        return {"id": post.id, "review_status": post.review_status}

    if post.review_status != "pending":
        raise HTTPException(
            status_code=409,
            detail=f"Post is already {post.review_status}, only pending posts can be reviewed",
        )

    post.review_status = new_status
    db.commit()
    return {"id": post.id, "review_status": post.review_status}


@router.post("/review/{post_id}/approve")
@limiter.limit("30/minute")
def approve_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    return _decide(db, post_id, "approved")


@router.post("/review/{post_id}/reject")
@limiter.limit("30/minute")
def reject_post(
    request: Request,
    post_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key),
):
    return _decide(db, post_id, "rejected")
