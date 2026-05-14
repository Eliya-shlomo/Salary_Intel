"""
Test cases לevaluation.

relevant_ids = IDs של פוסטים שצריכים להופיע בתוצאות.
אלה ה-IDs מהseed_data שלנו — בדוק ב-DB אם שונים.
"""

TEST_CASES = [
    {
        "query": "כמה מרוויח מפתח פרונטאנד בתל אביב?",
        "relevant_ids": [1],  # Frontend Developer
    },
    {
        "query": "שכר DevOps עם ניסיון בחברה גדולה",
        "relevant_ids": [2],  # DevOps
    },
    {
        "query": "כמה מקבל data scientist מתחיל?",
        "relevant_ids": [4],  # Data Scientist
    },
    {
        "query": "מה השכר של team lead בפינטק?",
        "relevant_ids": [3],  # Team Lead
    },
    {
        "query": "Python backend developer כמה מרוויח?",
        "relevant_ids": [5],  # Backend Developer
    },
]
