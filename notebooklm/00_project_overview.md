# Salary Intel — סקירת פרויקט (מסמך 00)

> מסמך זה הוא נקודת הכניסה. הוא מסביר מה הפרויקט עושה, איזו בעיה הוא פותר, ומה קורה מרגע שמשתמש מקליד שאלה ועד שהוא מקבל תשובה.

---

## 1. במשפט אחד

מערכת RAG (Retrieval-Augmented Generation) שעונה על שאלות שכר בעברית ("כמה מרוויח DevOps בכיר בתל אביב?") על בסיס פוסטים אמיתיים מקהילות ההייטק הישראליות — ומחזירה תשובה **מעוגנת במקורות**, לא תשובה שה-LLM המציא.

## 2. הבעיה שהפרויקט פותר

אם שואלים ChatGPT "כמה מרוויח Backend עם 3 שנים בישראל?" מקבלים מספר שנשמע סביר אבל אין מאחוריו שום מקור. זו הזיה (hallucination) עם ביטחון עצמי גבוה. הבעיה מורכבת משלושה חלקים:

1. **ידע לא עדכני** — נתוני האימון של המודל מקובעים בזמן. שכר בהייטק זז כל רבעון.
2. **אין מקורות** — אי אפשר לאמת את המספר.
3. **אין דאטה ישראלי איכותי** — השוק הישראלי קטן ומיוצג חלש במודלים גלובליים.

**הפתרון:** לא לשאול את המודל "מה אתה יודע", אלא לשלוף מהמסד פוסטים אמיתיים רלוונטיים ולתת למודל להגיד "לפי שלושת הפוסטים האלה, הטווח הוא X-Y". המודל הופך מ"מקור ידע" ל"מנוע סיכום מעוגן".

## 3. הזרימה המלאה (End-to-End)

```text
[1] משתמש מקליד שאלה בעברית ב-Next.js
        ↓  POST /api/query
[2] שכבת Next.js (proxy) — מוסיפה X-API-Key ומעבירה ל-backend
        ↓  POST /api/v1/query  (FastAPI)
[3] אימות API Key  →  Rate Limiting (10 בקשות לדקה לכל IP, נשמר ב-Redis)
        ↓
[4] QueryTracker נפתח — מודד latency ו-cost לכל שלב
        ↓
[5] RETRIEVAL (מקבילי, asyncio.gather):
      (א) get_embedding(query)   →  וקטור 1536 מ-OpenAI
      (ב) expand_query(query)    →  GPT מחזיר {role, tech, location}
        ↓
[6] שאילתת SQL אחת ב-PostgreSQL, כוללת:
      - Semantic CTE: דמיון קוסינוס עם pgvector (אופרטור <=>)
      - Keyword  CTE: התאמת מילות מפתח משוקללת (role=3, tech=2, location=1)
      - RRF CTE:      איחוד שתי הרשימות ב-Reciprocal Rank Fusion
      → מחזיר 10 מועמדים
        ↓
[7] RERANKING — GPT-4o-mini קורא את 10 המועמדים ומחזיר סדר חדש, לוקחים top-3
        ↓
[8] GENERATION — GPT-4o-mini מקבל את 3 הפוסטים כ-context + system prompt קשיח
      ("אל תמציא מספרים, ענה בעברית, תן טווח, ציין כמה פוסטים השתמשת")
        ↓
[9] QueryTracker.save() — שומר ל-query_logs: latency לכל שלב, tokens, עלות $
        ↓
[10] JSON חוזר: { answer, posts_used, sources[] }
        ↓
[11] ה-UI מציג את התשובה + כרטיסי מקורות עם אחוז התאמה
```

## 4. שני הצינורות של המערכת

מערכת RAG היא תמיד **שני** צינורות נפרדים. חשוב מאוד להגיד את זה בראיון:

### צינור א' — Ingestion (אופליין, לא בזמן אמת)

```text
טקסט גולמי של פוסט
   ↓
extract_salary_data()  — GPT מוציא JSON מובנה:
                          {role, salary, years_experience, company_stage, location, is_salary_post}
   ↓
ולידציה — שכר חייב להיות בין 3,000 ל-300,000 ₪, אחרת null
   ↓
_build_embedding_text() — מחבר raw_text + מטא-דאטה למחרוזת אחת
   ↓
get_embedding()  →  וקטור 1536
   ↓
INSERT ל-salary_posts (טקסט + מטא-דאטה + וקטור באותה שורה)
```

### צינור ב' — Query (אונליין, בזמן אמת)

זה מה שתואר בסעיף 3.

**למה זה חשוב?** כי זה מסביר את החלטת הארכיטקטורה המרכזית: העלות היקרה (LLM extraction + embedding) משולמת **פעם אחת בזמן ingestion**, ולא בכל שאילתה. בזמן שאילתה משלמים רק על embedding אחד של השאלה + 2 קריאות GPT.

## 5. מפת הקבצים

```text
salary-intel/
├── backend/
│   ├── app/
│   │   ├── main.py                  # אתחול FastAPI, CORS, rate limiter, health check
│   │   ├── api/routes.py            # 3 endpoints: /query, /ingest, /stats
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic Settings — קריאת env vars
│   │   │   ├── security.py          # verify_api_key — FastAPI Dependency
│   │   │   ├── rate_limiter.py      # slowapi + Redis
│   │   │   ├── query_logger.py      # QueryTracker — latency + cost per stage
│   │   │   ├── exceptions.py        # היררכיית שגיאות של הדומיין
│   │   │   └── logging.py           # logger מפורמט
│   │   ├── db/
│   │   │   ├── database.py          # engine + SessionLocal + Base
│   │   │   ├── models.py            # SalaryPost, QueryLog
│   │   │   └── init_db.py           # CREATE EXTENSION vector + create_all
│   │   ├── ingestion/
│   │   │   ├── extractor.py         # GPT → JSON מובנה מפוסט גולמי
│   │   │   ├── ingestor.py          # embed + save
│   │   │   ├── bulk_ingestor.py     # לולאה על רשימת פוסטים
│   │   │   ├── data_generator.py    # יצירת פוסטים סינתטיים ב-GPT
│   │   │   ├── sample_data.py       # seed ידני
│   │   │   └── real_data.py         # 12 פוסטים אמיתיים מקהילות
│   │   ├── rag/
│   │   │   ├── embeddings.py        # get_embedding / get_embeddings_batch
│   │   │   ├── query_parser.py      # expand_query — הרחבת שאילתה
│   │   │   ├── retriever.py         # ★ ליבת החיפוש ההיברידי + RRF
│   │   │   ├── reranker.py          # LLM reranking
│   │   │   ├── generator.py         # ★ האורקסטרטור של כל הצינור
│   │   │   ├── evaluator.py         # Hit Rate, MRR, NDCG
│   │   │   ├── qa_generator.py      # יצירת 50 מקרי בדיקה סינתטיים
│   │   │   └── test_cases.py        # 5 מקרי בדיקה ידניים (ישן)
│   │   ├── ablation_study.py        # ★ השוואת 4 גרסאות של הצינור
│   │   └── generated_test_cases.json# 50 זוגות שאלה↔פוסט
│   ├── Dockerfile
│   ├── render.yaml                  # deployment ל-Render
│   └── requirements.txt
├── frontend/                        # Next.js 16 + React 19 + TypeScript
│   ├── app/page.tsx                 # ה-UI כולו (client component)
│   ├── app/api/query/route.ts       # שכבת proxy להסתרת ה-API key
│   └── lib/api.ts                   # פונקציית fetch
└── docker-compose.yml               # db (pgvector) + redis + api
```

שלושת הקבצים שהכי חשוב להכיר לעומק לראיון: `retriever.py`, `generator.py`, `ablation_study.py`.

## 6. מהלך הפרויקט — סדר הבנייה לפי ההיסטוריה בגיט

זה הסיפור שמספרים בראיון. הוא מראה חשיבה אינקרמנטלית, לא "בניתי הכל ביום".

| # | Commit | מה נוסף | למה בשלב הזה |
|---|--------|---------|---------------|
| 1 | `47a` initialize db, fastapi, embedding, ingest | שלד: DB + API + embedding + הכנסת פוסט | קודם כל להוכיח שהצינור הבסיסי עובד end-to-end |
| 2 | `4f8` added ranker, keyword search, logs, exceptions | חיפוש היברידי + reranker + query parser | חיפוש סמנטי לבד פספס מונחים טכניים מדויקים |
| 3 | `e0c` docker-compose up | קונטיינריזציה | להפוך את הסביבה לשחזורית |
| 4 | `78c` frontend ready | Next.js UI | לתת פנים למוצר |
| 5 | `ff0` extractor + bulk ingestor + fabric data | הכנסת דאטה בכמות | 5 פוסטים לא מספיקים כדי לבדוק retrieval |
| 6 | `ced` render deployment config | תצורת דיפלוי | |
| 7 | `5eb` rate limiting | slowapi + Redis | ה-endpoint עולה כסף אמיתי לכל קריאה |
| 8 | `bbf` + `b86` API key security + proxy layer | הגנה על המפתח | הדפדפן לא אמור לראות סוד |
| 9 | `554` query logger | QueryTracker | "אי אפשר לשפר מה שלא מודדים" |
| 10 | `07c` async parallelism | asyncio.gather | המדידה חשפה ש-retrieval לוקח 5 שניות |
| 11 | `e16` expand test set 5→50 | qa_generator | 5 מקרי בדיקה = רעש סטטיסטי |

**הסיפור שמאחורי הרשימה:** בניתי → מדדתי → גיליתי צוואר בקבוק → תיקנתי → מדדתי שוב. זה בדיוק מה שמראיין רוצה לשמוע.

## 7. המספרים שחייבים לזכור בעל פה

| מדד | ערך |
|---|---|
| מודל embedding | `text-embedding-3-small`, 1536 מימדים |
| מודל LLM | `gpt-4o-mini` (גם ל-expansion, גם ל-rerank, גם ל-generation, גם ל-extraction) |
| סף דמיון (threshold) | 0.25 |
| קבוע RRF | k = 60 |
| משקולות keyword | role=3, tech=2, location=1 |
| מועמדים מ-retrieval | 10 |
| פוסטים אחרי rerank | 3 |
| Rate limit | 10/דקה על query, 5/דקה על ingest, 30/דקה על stats |
| Latency לפני אופטימיזציה | retrieval 5.0s, total 6.9s |
| Latency אחרי asyncio.gather | retrieval 1.9s (-62%), total 5.1s (-26%) |
| עלות משוערת לשאילתה | ~$0.000085 |
| תמחור gpt-4o-mini | $0.15 / 1M input tokens, $0.60 / 1M output |
| מקרי בדיקה | 50 (סינתטיים, נוצרו מהפוסטים עצמם) |
| טמפרטורה | 0 ב-expansion/rerank/extraction, 0.3 ב-generation, 0.8 ביצירת דאטה |
