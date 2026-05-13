import sys
sys.path.append(".")

from app.rag.embeddings import get_embedding

embedding = get_embedding("מפתח React עם 4 שנות ניסיון בתל אביב")

print(f"✓ אורך הוקטור: {len(embedding)}")
print(f"✓ 5 ערכים ראשונים: {embedding[:5]}")
