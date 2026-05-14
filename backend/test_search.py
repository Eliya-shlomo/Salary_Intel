import sys
sys.path.append(".")
from app.rag.retriever import search_similar_posts
from app.rag.retriever import _sanitize_keyword


queries = [
    "כמה מרוויח מפתח פרונטאנד בתל אביב?",
    "שכר DevOps עם ניסיון בחברה גדולה",
    "כמה מקבל data scientist מתחיל?",
    "כמה מרוויח DevOps בכיר?",
]

for query in queries:
    print(f"\n🔍 {query}")
    print("-" * 50)

    results = search_similar_posts(query, limit=3)

    if not results:
        print("  אין תוצאות מעל threshold")
        continue

    for r in results:
        print(
            f"  rrf: {r['rrf_score']} | "
            f"semantic: {r['similarity']} | "
            f"{r['role']} | "
            f"{r['salary']}₪"
        )




dangerous_inputs = [
    "devops'; DROP TABLE salary_posts; --",
    "react\"; DELETE FROM salary_posts; --",
    "python' OR '1'='1",
    "תל אביב",        # תקין — אמור לעבור
    "React Developer", # תקין — אמור לעבור
]

print("\n🔒 בדיקת SQL Injection Protection:")
for inp in dangerous_inputs:
    cleaned = _sanitize_keyword(inp)
    print(f"  '{inp[:40]}' → '{cleaned}'")

