import sys
sys.path.append(".")

from app.rag.generator import answer_salary_query

queries = [
    "כמה מרוויח מפתח פרונטאנד עם 4 שנות ניסיון בתל אביב?",
    "מה השכר של DevOps בכיר?",
    "כמה מקבל data scientist מתחיל?",
]

for query in queries:
    print(f"\n{'='*60}")
    print(f"שאלה: {query}")
    print('='*60)
    result = answer_salary_query(query)
    print(f"\nתשובה:\n{result['answer']}")