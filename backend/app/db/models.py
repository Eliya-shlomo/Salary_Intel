from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db.database import Base

class SalaryPost(Base):
    __tablename__ = "salary_posts"

    # מזהה
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # תוכן
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    role: Mapped[str | None] = mapped_column(String(100))
    years_experience: Mapped[float | None] = mapped_column(Float)
    salary: Mapped[float | None] = mapped_column(Float)
    company_stage: Mapped[str | None] = mapped_column(String(50))
    location: Mapped[str | None] = mapped_column(String(100))

    # וקטור לחיפוש סמנטי — 1536 זה הגודל של OpenAI embeddings
    embedding: Mapped[list | None] = mapped_column(Vector(1536))

    # מקור ותאריך
    source: Mapped[str | None] = mapped_column(String(100))
    post_date: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow
    )


