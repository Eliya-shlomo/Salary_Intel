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