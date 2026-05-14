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