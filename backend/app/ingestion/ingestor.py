from sqlalchemy.orm import Session
from app.db.models import SalaryPost
from app.rag.embeddings import get_embedding
from app.db.database import SessionLocal
from datetime import datetime

def ingest_post(
    raw_text: str,
    role: str | None = None,
    years_experience: float | None = None,
    salary: float | None = None,
    company_stage: str | None = None,
    location: str | None = None,
    source: str = "manual",
    post_date: datetime | None = None,
) -> SalaryPost:
    """
    קולט פוסט אחד, יוצר embedding ושומר במסד.
    """
    # טקסט שנכנס ל-embedding: שילוב של כל המידע
    # למה? כי ככה החיפוש מוצא לפי הקשר מלא
    embedding_text = _build_embedding_text(
        raw_text, role, years_experience, salary, location
    )
    
    embedding = get_embedding(embedding_text)
    
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
    
    db: Session = SessionLocal()
    try:
        db.add(post)
        db.commit()
        db.refresh(post)
        return post
    finally:
        db.close()


def _build_embedding_text(
    raw_text: str,
    role: str | None,
    years_experience: float | None,
    salary: float | None,
    location: str | None,
) -> str:
    """
    בונה טקסט מועשר ל-embedding.
    
    למה לא רק raw_text?
    כי embedding של "28K React תל אביב 4 שנים" 
    יותר קרוב לשאלות רלוונטיות מאשר פוסט גולמי מלא ברעש.
    """
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
