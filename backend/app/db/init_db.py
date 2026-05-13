from app.db.database import engine
from app.db.models import Base
from sqlalchemy import text

def init_db():
    # הפעל את תוסף pgvector
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    
    # צור את כל הטבלאות
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")

if __name__ == "__main__":
    init_db()
