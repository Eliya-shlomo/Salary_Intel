import sys
sys.path.append(".")

from app.ingestion.ingestor import ingest_post
from app.ingestion.sample_data import SAMPLE_POSTS

def seed():
    print(f"מכניס {len(SAMPLE_POSTS)} פוסטים...")
    
    for i, post in enumerate(SAMPLE_POSTS):
        result = ingest_post(**post)
        print(f"✓ [{i+1}] {result.role} — {result.salary}₪  (id: {result.id})")
    
    print("\n✓ הכל נשמר במסד")

if __name__ == "__main__":
    seed()
