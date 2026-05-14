from sqlalchemy.orm import Session
from app.db.models import SalaryPost
from app.rag.embeddings import get_embedding
from app.db.database import SessionLocal
from app.ingestion.extractor import extract_salary_data
from app.core.logging import get_logger
from app.core.exceptions import SalaryIntelError
from datetime import datetime

logger = get_logger(__name__)


def ingest_post(
    raw_text: str,
    role: str | None = None,
    years_experience: float | None = None,
    salary: float | None = None,
    company_stage: str | None = None,
    location: str | None = None,
    source: str = "manual",
    post_date: datetime | None = None,
    auto_extract: bool = False,  # ← חדש
) -> SalaryPost:
    """
    קולט פוסט אחד, יוצר embedding ושומר במסד.

    אם auto_extract=True — מחלץ מטאדאטה אוטומטית מהטקסט.
    שימושי לנתונים גולמיים מפייסבוק.
    """
    if not raw_text or not raw_text.strip():
        raise ValueError("טקסט ריק — לא ניתן לקלוט")

    # חילוץ אוטומטי אם ביקשו
    if auto_extract:
        logger.info("מחלץ מטאדאטה אוטומטית...")
        extracted = extract_salary_data(raw_text)

        if not extracted["is_salary_post"]:
            logger.warning("הפוסט לא עוסק בשכר — מדלג")
            raise ValueError("הפוסט לא עוסק בשכר")

        # השתמש בחילוץ רק אם לא סופקו ידנית
        role = role or extracted["role"]
        salary = salary or extracted["salary"]
        years_experience = years_experience or extracted["years_experience"]
        company_stage = company_stage or extracted["company_stage"]
        location = location or extracted["location"]

    logger.info(f"קולט: {role} | {salary}₪")

    try:
        embedding_text = _build_embedding_text(
            raw_text, role, years_experience, salary, location
        )
        embedding = get_embedding(embedding_text)
    except Exception as e:
        logger.error(f"נכשל ביצירת embedding: {e}")
        raise SalaryIntelError("לא ניתן לעבד את הפוסט")

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
        logger.info(f"נשמר | id={post.id}")
        return post

    except Exception as e:
        db.rollback()
        logger.error(f"שגיאת DB: {e}")
        raise SalaryIntelError("שגיאה בשמירת הפוסט")
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
        parts.append(f"תפקיד: {role}")
    if years_experience:
        parts.append(f"ניסיון: {years_experience} שנים")
    if salary:
        parts.append(f"שכר: {salary}")
    if location:
        parts.append(f"מיקום: {location}")
    return " | ".join(parts)