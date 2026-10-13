# פערים ידועים, באגים, ו-Roadmap (מסמך 05)

> **תקרא את זה לפני הראיון.** מראיין טוב ימצא את הדברים האלה. עדיף שתגיע אליהם ראשון — זה הופך חולשה להוכחת בגרות הנדסית.
> העיקרון: **"אני יודע שזו בעיה, זו הסיבה שלא טיפלתי בה עדיין, וכך הייתי מתקן"** מנצח כל תשובה מתחמקת.

---

## חלק א' — באגים אמיתיים בקוד (לתקן לפני הראיון)

### 🔴 באג 1 — שכבת ה-Proxy ב-Frontend לא פעילה

**מה קרה:** התוכן של שני קבצים התחלף.

- `frontend/app/api/query/route.ts` — אמור להיות **Route Handler** של Next (עם `export async function POST(req)`). בפועל הוא מכיל את **קוד הלקוח** — הפונקציה `querySalary` שקוראת ל-`/api/query`.
- `frontend/lib/api.ts` — מכיל עדיין את **הגרסה הישנה** שקוראת ישירות ל-backend עם `NEXT_PUBLIC_API_KEY`.
- `frontend/app/page.tsx` מייבא מ-`@/lib/api`.

**התוצאה:** האפליקציה עוקפת את ה-proxy לגמרי וחושפת את ה-API key בדפדפן — בדיוק הבעיה שהקומיט `b86e5fe` נועד לפתור.

**התיקון:**

`frontend/lib/api.ts` — קוד הלקוח (בלי סודות):
```ts
export interface Source {
  id: number; role: string; salary: number;
  years_experience: number; location: string;
  raw_text: string; similarity: number;
}

export interface QueryResponse {
  answer: string; posts_used: number; sources: Source[];
}

export async function querySalary(query: string): Promise<QueryResponse> {
  const response = await fetch("/api/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Server error");
  }
  return response.json();
}
```

`frontend/app/api/query/route.ts` — ה-Route Handler האמיתי (רץ בשרת):
```ts
import { NextRequest, NextResponse } from "next/server";

const API_URL = process.env.API_URL ?? "http://localhost:8000";
const API_KEY = process.env.API_KEY;   // ללא NEXT_PUBLIC — לא מגיע לדפדפן

export async function POST(req: NextRequest) {
  const body = await req.json();

  const upstream = await fetch(`${API_URL}/api/v1/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": API_KEY ?? "",
    },
    body: JSON.stringify(body),
  });

  const data = await upstream.json();
  return NextResponse.json(data, { status: upstream.status });
}
```

**ואם אין זמן לתקן:** דע להסביר בדיוק את מה שכתוב כאן. "יש לי באג ידוע ב-frontend — הקבצים התחלפו בקומיט האחרון וה-proxy לא פעיל בפועל. אני יודע מה התיקון." זה בסדר גמור.

---

### 🔴 באג 2 — `evaluator.py` שבור אחרי המעבר ל-async

`app/rag/evaluator.py:73`:
```python
results = search_similar_posts(query, limit=k)   # ← מחזיר coroutine, לא רשימה
```

`search_similar_posts` הפכה ל-`async` בקומיט `07cf9cb`, אבל `evaluate_retrieval` נשארה סינכרונית ולא מוסיפה `await`. הפונקציה תקרוס על `results[:k]`.

**התיקון:** להפוך את `evaluate_retrieval` ל-`async def` ולהוסיף `await`:
```python
async def evaluate_retrieval(test_cases: list[dict], k: int = 3) -> dict:
    ...
    results = await search_similar_posts(query, limit=k)
```

**הערה:** `ablation_study.py` **לא** מושפע — הוא מריץ לולאת eval משלו עם `await` תקין. כלומר ה-ablation עובד וה-evaluator העצמאי לא. אם אין זמן — הרץ את ה-ablation, הוא המשמעותי מהשניים.

---

### 🟡 באג 3 — מילות מפתח מסוג `tech` כמעט לא עובדות

`app/rag/retriever.py:132-137`:
```python
f"CASE WHEN LOWER(role) LIKE '%{safe_kw}%' "
f"OR LOWER(company_stage) LIKE '%{safe_kw}%' ..."
```

מילות מפתח טכנולוגיות ("kubernetes", "react") מחופשות מול `role` ומול `company_stage`. אבל `company_stage` מכיל רק "Startup"/"Series A"/"Enterprise" — **הוא לעולם לא יכיל שם טכנולוגיה**. אין עמודת `tech` בסכמה.

**התוצאה:** המשקל 2 של `tech` כמעט לא מייצר התאמות. הקטגוריה כמעט חסרת השפעה.

**התיקון:** אפשרות א' — לחפש גם ב-`raw_text` (שם הטכנולוגיות באמת מוזכרות). אפשרות ב' — להוסיף עמודת `tech_stack` מסוג מערך שה-extractor ימלא, ולחפש בה.

**למה זה שווה לדעת:** זו דוגמה מצוינת לפער בין הכוונה למימוש, ולערך של ablation — ריצה של ה-ablation הייתה מראה שגרסה 3 (עם expansion) לא משתפרת כמצופה, וזה היה מוביל לגילוי.

---

### 🟡 באג 4 — מעקב עלות חלקי

`QueryTracker.add_tokens` נקרא רק ב-`generator.py` אחרי ה-generation. הטוקנים של ה-**query expansion** וה-**reranking** לא נספרים כלל.

**התוצאה:** `estimated_cost_usd` בטבלה נמוך פי ~2-3 מהעלות האמיתית.

**התיקון:** להחזיר את `response.usage` גם מ-`expand_query` ומ-`rerank_results`, ולקרוא ל-`tracker.add_tokens` עבור כל אחד.

---

### 🟡 באג 5 — קבצי בדיקה נמחקו ולא נוקו

`git status` מראה:
```text
D backend/run_evaluation.py
D backend/test_extractor.py
D backend/test_search.py
```

הקבצים נמחקו מהדיסק אבל המחיקה לא נכנסה לקומיט. **בפועל אין בפרויקט אף בדיקה אוטומטית.**

**מה לעשות:** או לקמט את המחיקה (`git add -A && git commit`), או — עדיף — להוסיף כמה טסטים אמיתיים ב-pytest (ראה חלק ג').

---

## חלק ב' — פערים ארכיטקטוניים (לא באגים, אבל חוסרים אמיתיים)

| # | הפער | ההשלכה | התיקון | דחיפות |
|---|---|---|---|---|
| 1 | **אין טסטים** | כל refactor הוא הימור | pytest + httpx TestClient, mock ל-OpenAI | 🔴 גבוהה |
| 2 | **אין מיגרציות** | `create_all` לא מטפל בשינוי סכמה — חוסם בפרודקשן | Alembic | 🔴 גבוהה |
| 3 | **סניטציה במקום פרמטריזציה** | חשיפת SQL injection נשארת פתוחה תיאורטית | `ANY(:keywords)` / `unnest()` | 🔴 גבוהה |
| 4 | **אין cache** | כל שאילתה חוזרת עולה מלא ולוקחת 5 שניות | Redis על embeddings ועל תשובות | 🟠 בינונית |
| 5 | **אין אינדקס וקטורי** | סריקה מלאה בכל שאילתה | `CREATE INDEX USING hnsw (embedding vector_cosine_ops)` | 🟠 בינונית |
| 6 | **DB סינכרוני ב-app async** | חוסם את ה-event loop | asyncpg + AsyncSession | 🟠 בינונית |
| 7 | **אין retry / circuit breaker** | שגיאה חולפת של OpenAI = כישלון מיידי | tenacity עם exponential backoff | 🟠 בינונית |
| 8 | **אין אימות משתמשים** | מפתח יחיד משותף, אין מכסה פר-משתמש | JWT / session | 🟠 בינונית |
| 9 | **אין הערכת generation** | לא הייתי מזהה הזיה | RAGAS faithfulness, או guardrail מספרי | 🟠 בינונית |
| 10 | **אין streaming** | המשתמש מחכה 5 שניות למסך ריק | `stream=True` + SSE | 🟡 נמוכה |
| 11 | **אין chunking** | פוסטים ארוכים מתמהלים סמנטית | chunking עם overlap לפוסטים ארוכים | 🟡 נמוכה |
| 12 | **פרמטרים לא מכוילים** | 3/2/1, threshold=0.25, top_k=3 — כולם אינטואיציה | grid search על סט הבדיקה הקיים | 🟡 נמוכה |
| 13 | **סיסמאות בקוד** | `postgres/postgres` ב-docker-compose | secrets management | 🟡 נמוכה (dev בלבד) |
| 14 | **CORS נעול ל-localhost** | לא יעבוד בפרודקשן | לקרוא origins מ-config | 🟡 נמוכה |

---

## חלק ג' — הטסטים שהייתי כותב

זו שאלה שיכולה להישאל ("איך היית בודק את זה?"). כדאי שתהיה תשובה מובנית:

| רמה | מה בודקים | דוגמאות |
|---|---|---|
| **Unit** | לוגיקה טהורה, בלי רשת | `_sanitize_keyword` מסיר גרשיים ומקצר ל-50; `hit_rate_at_k` מחזיר 1.0 כשיש התאמה; `reciprocal_rank` מחזיר 0.5 למקום 2; `_build_embedding_text` מדלג על שדות None |
| **Integration** | עם DB, בלי OpenAI (mock) | `search_similar_posts` מחזירה תוצאות ממוינות; `ingest_post` שומר עם וקטור בגודל 1536; ולידציית שכר מחוץ לטווח מחזירה None |
| **API** | `httpx.AsyncClient` מול האפליקציה | 401 בלי API key; 400 על שאילתה ריקה; 200 עם `answer`/`sources`/`posts_used`; 429 אחרי חריגת rate limit |
| **Regression** | על סט הבדיקה | ה-ablation רץ ומוודא ש-MRR לא ירד מתחת לסף מוסכם |

**המשפט לראיון:** "כתיבת טסטים למערכת LLM היא לא טריוויאלית כי הפלט לא דטרמיניסטי. הפתרון הוא לפצל: את הלוגיקה הדטרמיניסטית — RRF, המדדים, הסניטציה, בניית ה-context — בודקים ב-unit tests רגילים. את קריאות ה-LLM עוטפים ב-mock ובודקים שהצינור מטפל נכון בפלט תקין וגם בפלט פגום. ואת האיכות הכוללת מודדים ב-eval על סט בדיקה — זה לא test שעובר או נכשל, זה מדד שעוקבים אחריו לאורך זמן."

---

## חלק ד' — Roadmap מסודר

### שלב 1 — חוב טכני (שבוע)
1. פרמטריזציה מלאה של שאילתת מילות המפתח
2. Alembic למיגרציות
3. חבילת pytest בסיסית + CI
4. תיקון `evaluator.py` ותיקון קבצי ה-frontend
5. השלמת מעקב הטוקנים לכל שלבי הצינור

### שלב 2 — ביצועים ועלות (שבוע)
1. Redis cache על embeddings (מפתח: hash של הטקסט)
2. Redis cache על תשובות מלאות (TTL של שעות)
3. Streaming של ה-generation
4. אינדקס HNSW
5. tenacity retry עם exponential backoff

### שלב 3 — איכות (שבוע)
1. ingestion אמיתי ממקורות ציבוריים
2. סט בדיקה מתויג ידנית מתוך `query_logs`
3. הערכת generation — RAGAS faithfulness + guardrail מספרי
4. grid search על המשקולות, ה-threshold ו-top_k
5. תיקון קטגוריית ה-tech (עמודת `tech_stack`)

### שלב 4 — מוצר (שבוע)
1. אימות משתמשים + מכסה פר-משתמש
2. סינון לפי שנות ניסיון/מיקום ב-UI
3. ניתוח מגמות שכר לאורך זמן (יש כבר `post_date`!)
4. דשבורד אדמין מעל `query_logs`

---

## חלק ה' — הניסוח לראיון

כשמראיין מוצא חולשה, זה הפורמט:

> **"נכון, וזה מודע. [הנימוק למה זה בסדר בקנה המידה הנוכחי]. הדרך הנכונה היא [הפתרון הספציפי], וזה ה-item ה-X ברשימה שלי."**

דוגמאות מוכנות:

- *"אין לך טסטים"* → "נכון. בניתי במקום זה evaluation pipeline, כי בפרויקט LLM המדד המשמעותי הוא איכות retrieval ולא coverage. אבל זו לא תשובה מלאה — הלוגיקה הדטרמיניסטית שלי, ה-RRF והמדדים והסניטציה, צריכה unit tests רגילים. זה ה-item הראשון ברשימה."

- *"הסניטציה שלך לא מספיקה"* → "מסכים. היא עובדת אבל היא לא הפתרון הנכון — פרמטריזציה טובה מכל סניטציה. הייתי מעביר את מילות המפתח כמערך עם `ANY(:keywords)`. נקודה מקלה: המקור הוא פלט GPT בסכמה מוגבלת ולא קלט משתמש ישיר, אבל זה מקטין את משטח התקיפה ולא סוגר אותו."

- *"למה אין cache?"* → "כי מדדתי קודם ובניתי את התשתית למדידה לפני האופטימיזציות. ה-cache הוא הצעד הבא והכי משתלם — Redis כבר בסטאק בשביל ה-rate limiting, ושאילתות שכר חוזרות מאוד."
