import sys
sys.path.append(".")

from app.ingestion.extractor import extract_salary_data

posts = [
    "היי, מפתח React עם 4 שנים, קיבלתי הצעה של 28K מסטארטאפ בתל אביב. הגיוני?",
    "DevOps עם 6 שנות ניסיון, חברה פיננסית גדולה. מרוויח 42K + בונוס שנתי.",
    "מישהו יודע מסעדה טובה בתל אביב?",  # לא פוסט שכר
]

for post in posts:
    print(f"\nפוסט: {post[:50]}...")
    result = extract_salary_data(post)
    print(f"תוצאה: {result}")