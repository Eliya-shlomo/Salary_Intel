"""Seed the database with posts.

Runs inside the container (app/ is mounted, so no rebuild needed):
    docker exec salary_intel_api python -m app.seed
    docker exec salary_intel_api python -m app.seed --real

Replaces backend/seed_data.py, which is not copied into the image
and calls the async ingest_post without awaiting it.
"""
import asyncio
import sys

from app.db.database import SessionLocal
from app.db.models import SalaryPost
from app.ingestion.ingestor import ingest_post
from app.ingestion.sample_data import SAMPLE_POSTS


def count_posts() -> int:
    db = SessionLocal()
    try:
        return db.query(SalaryPost).count()
    finally:
        db.close()


async def seed(include_real: bool = False) -> None:
    existing = count_posts()
    if existing:
        print(f"database already holds {existing} posts - nothing to do")
        return

    print(f"ingesting {len(SAMPLE_POSTS)} sample posts...")
    for i, post in enumerate(SAMPLE_POSTS, 1):
        saved = await ingest_post(**post)
        print(f"  [{i}] id={saved.id}  {saved.role}  {saved.salary}")

    if include_real:
        from app.ingestion.bulk_ingestor import bulk_ingest
        from app.ingestion.real_data import REAL_POSTS

        print(f"\nbulk ingesting {len(REAL_POSTS)} real posts (LLM extraction)...")
        print(await bulk_ingest(REAL_POSTS, source="manual_paste"))

    print(f"\ndone - {count_posts()} posts in the database")


if __name__ == "__main__":
    asyncio.run(seed(include_real="--real" in sys.argv))
