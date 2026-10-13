# צלילה לעומק — צינור ה-RAG שלב אחר שלב (מסמך 02)

> כאן מסבירים **מה קורה בפועל בקוד**. לכל שלב: התיאוריה, המימוש שלי, ולמה בחרתי כך.

---

## רקע: מה זה RAG ולמה לא Fine-tuning

**RAG** = Retrieval-Augmented Generation. במקום לסמוך על מה שהמודל "יודע" מהאימון, שולפים מסמכים רלוונטיים ממקור חיצוני ומדביקים אותם ל-prompt. המודל עונה **על סמך מה שנתנו לו**.

**שלוש הפרדיגמות** (לפי סקירת Gao et al. שנמצאת ב-`rag.md`):

| פרדיגמה | מה זה | איפה אני |
|---|---|---|
| **Naive RAG** | Index → Retrieve → Read. חיפוש וקטורי פשוט, top-k, לתוך ה-prompt | לא — עברתי את זה |
| **Advanced RAG** | מוסיפים pre-retrieval (query rewriting/expansion) ו-post-retrieval (reranking, compression) | ✅ **כאן אני** |
| **Modular RAG** | מודולים ניתנים להחלפה, אחזור איטרטיבי/רקורסיבי/אדפטיבי, agents | לא — הצעד הבא |

**למה RAG ולא Fine-tuning:**

| קריטריון | RAG | Fine-tuning |
|---|---|---|
| עדכון דאטה | `INSERT` בודד, זמין מיד | אימון מחדש של המודל |
| עלות עדכון | ~$0.00002 לפוסט | מאות דולרים לריצה |
| מקורות ואימות | מחזיר את הפוסטים עצמם | קופסה שחורה |
| הזיות | מוגבל ע"י ה-context | המודל עדיין ממציא |
| מה זה טוב בשבילו | **ידע** | **התנהגות/סגנון/פורמט** |

**המשפט לראיון:** "Fine-tuning מלמד את המודל *איך* לדבר. RAG נותן לו *מה* לדעת. שכר בהייטק זה ידע שמשתנה כל הזמן — לכן RAG. אם הייתי רוצה שהתשובות תמיד יהיו בפורמט מסוים ובסגנון מסוים, שם fine-tuning היה עוזר."

---

## שלב 0 — Ingestion: איך דאטה נכנס למערכת

קובץ: `app/ingestion/extractor.py` + `app/ingestion/ingestor.py`

### 0.1 Extraction — GPT כמנתח מובנה

פוסט אמיתי נראה כך:

```text
"מהנדס Devops בסטארטאפ. 62 א׳ ברוטו + אופציות. יומיים מהבית. עשור ניסיון"
```

`extract_salary_data()` שולח את הטקסט ל-GPT עם system prompt שמכתיב סכמת JSON קשיחה, ומקבל:

```json
{
  "role": "DevOps Engineer",
  "salary": 62000,
  "years_experience": 10,
  "company_stage": "Startup",
  "location": null,
  "is_salary_post": true
}
```

**למה LLM ולא regex?** כי הטקסט הוא עברית מדוברת עם ואריאציות אינסופיות: "62 א׳", "62K", "שישים ושתיים אלף", "עשור ניסיון" (=10 שנים). regex היה שביר לחלוטין. ה-LLM מנרמל את הכל לסכמה אחידה.

**שלוש הגנות במימוש:**
1. `temperature=0` — פלט דטרמיניסטי, אין יצירתיות ב-extraction.
2. **ולידציה של טווח** — `MIN_SALARY=3000`, `MAX_SALARY=300000`. אם ה-LLM מחזיר `62` (במקום 62000) או `6200000`, הערך הופך ל-`null` במקום לזהם את המסד.
3. **fallback על JSON פגום** — `json.JSONDecodeError` מוחזר כאובייקט ריק עם `is_salary_post: false`, לא זורק חריגה שמפילה את הצינור.

**דגל `is_salary_post`** — מסנן זבל. פוסט על "איך לעבור ראיון" נדחה לפני שהוא מגיע למסד.

### 0.2 בניית טקסט ה-Embedding

```python
def _build_embedding_text(raw_text, role, years_experience, salary, location):
    parts = [raw_text]
    if role: parts.append(f"Role: {role}")
    ...
    return " | ".join(parts)
```

**זו החלטת עיצוב חשובה.** אני לא מבצע embedding לטקסט הגולמי בלבד — אני מחבר אליו את המטא-דאטה המנורמל. למה? כי הפוסט הגולמי אומר "מהנדס Devops" בעברית, אבל השאילתה עשויה לומר "DevOps Engineer" באנגלית. הוספת `Role: DevOps Engineer` לטקסט מכניסה את הצורה המנורמלת לתוך הווקטור עצמו, ומשפרת התאמה חוצת-שפות.

### 0.3 אין Chunking — ולמה זה בסדר

ברוב מערכות ה-RAG מפצלים מסמכים ארוכים ל-chunks. אצלי **כל פוסט הוא chunk אחד**.

**הנימוק:** פוסט שכר הוא יחידת מידע אטומית — התפקיד, השכר והניסיון קשורים זה לזה. פיצול "DevOps, 6 שנים" מ-"55K" היה הורס את המשמעות. גודל טיפוסי הוא 50-200 טוקנים, הרבה מתחת למגבלה.

**מתי זה יישבר:** בפוסטים ארוכים כמו אלה שיש לי ב-`real_data.py` (למשל פוסט על תכנון פנסיוני עם 15 שורות) — הווקטור מתמהל בין נושאים. שם chunking היה עוזר.

---

## שלב 1 — Query Expansion (pre-retrieval)

קובץ: `app/rag/query_parser.py`

### הבעיה

השאלה "כמה מרוויח DevOps בכיר בתל אביב?" מכילה מילים חסרות משמעות לחיפוש ("כמה", "מרוויח") ומילות מפתח קריטיות שפזורות בה. חיפוש מילות מפתח על המחרוזת המלאה יכשל.

### הפתרון

GPT מקבל את השאלה ומחזיר קטגוריזציה מובנית:

```json
{
  "role": ["devops", "devops engineer", "מהנדס devops"],
  "tech": ["aws", "kubernetes"],
  "location": ["תל אביב"]
}
```

**למה שלוש קטגוריות ולא רשימה שטוחה?** כי הן **לא שוות ערך**. התאמה על `role` אומרת הרבה יותר על רלוונטיות מהתאמה על `location` — יש אלפי אנשים בתל אביב אבל השאלה היא על DevOps. הקטגוריזציה מאפשרת את השקלול בשלב הבא.

**החלטות במימוש:**
- `temperature=0` — יציבות.
- `max_tokens=150` — הפלט קצר, אין סיבה לשלם על יותר.
- הנחיה למודל: "role בעברית ובאנגלית" — מכסה את שתי השפות.
- מגבלות (max 3 role, max 3 tech, max 2 location) — מונע התפוצצות של תנאי ה-SQL.
- `.lower()` על הכל — התאמה case-insensitive.
- `try/except` שמחזיר קטגוריות ריקות — אם ה-expansion נכשל, החיפוש הסמנטי לבדו עדיין עובד. **degradation, not failure.**

---

## שלב 2 — Hybrid Search (הליבה)

קובץ: `app/rag/retriever.py` — הקובץ הכי חשוב בפרויקט.

### 2.1 למה היברידי בכלל

| שיטה | חזקה ב- | נכשלת ב- |
|---|---|---|
| **סמנטי (וקטורי)** | מילים נרדפות, ניסוח שונה. "מהנדס תשתיות" ≈ "DevOps" | מונחים מדויקים ונדירים. "Kubernetes" ו-"Docker" קרובים במרחב הווקטורי אבל הם לא אותו דבר |
| **מילות מפתח** | התאמה מדויקת. "React" מוצא בדיוק React | ניסוח שונה. "פרונטאנד" לא מוצא "Frontend" |

השילוב מכסה את החולשות של שניהם. זה נקרא בספרות **hybrid retrieval**, וזו אחת הטכניקות הכי מבוססות ב-Advanced RAG.

### 2.2 אופטימיזציית ה-async — הסיפור הכי טוב לראיון

```python
# לפני — סדרתי, ~5.0 שניות
query_embedding = await get_embedding(query)   # ~0.5s
keywords = await expand_query(query)           # ~1.4s

# אחרי — מקבילי, ~1.9 שניות
query_embedding, keywords = await asyncio.gather(
    get_embedding(query),
    expand_query(query)
)
```

**התובנה:** שתי הקריאות **לא תלויות זו בזו**. שתיהן מקבלות את אותו input (השאלה) ומייצרות פלטים נפרדים. אין שום סיבה להריץ אותן בטור.

**התוצאה:** retrieval ירד מ-5.0s ל-1.9s (**-62%**), total מ-6.9s ל-5.1s (**-26%**).

**המשמעות העמוקה יותר:** צוואר הבקבוק **עבר** — עכשיו השלב האיטי הוא ה-generation. זה בדיוק מה שאופטימיזציה טובה עושה: היא לא רק מאיצה, היא מזיזה את הבעיה למקום הבא, וזה אומר שהמדידה הבאה תהיה על ה-generation.

**איך גיליתי את זה?** דרך `QueryTracker` שמודד latency לכל שלב בנפרד. בלי המדידה לא הייתי יודע ש-retrieval הוא האשם.

### 2.3 שאילתת ה-SQL — פירוק ל-CTE-ים

```sql
WITH semantic AS (
    SELECT id,
           1 - (embedding <=> CAST(:embedding AS vector)) AS similarity,
           ROW_NUMBER() OVER (ORDER BY embedding <=> CAST(:embedding AS vector)) AS rank
    FROM salary_posts
    WHERE 1 - (embedding <=> CAST(:embedding AS vector)) > :threshold
),
```

**CTE 1 — `semantic`:** מחשב cosine similarity לכל שורה, מסנן מתחת ל-`threshold` (0.25), ומייצר **דירוג** (`ROW_NUMBER`). הדירוג — לא הציון — הוא מה שיזין את ה-RRF.

```sql
keyword AS (
    SELECT id, ROW_NUMBER() OVER (ORDER BY weighted_score DESC) AS rank
    FROM (
        SELECT id, (CASE WHEN LOWER(role) LIKE '%devops%' THEN 3 ELSE 0 END +
                    CASE WHEN LOWER(location) LIKE '%תל אביב%' THEN 1 ELSE 0 END) AS weighted_score
        FROM salary_posts
        WHERE (...) > 0
    ) scored
),
```

**CTE 2 — `keyword`:** ציון משוקלל לפי סוג ההתאמה, גם הוא מומר לדירוג.

```sql
rrf AS (
    SELECT COALESCE(s.id, k.id) AS id,
           COALESCE(1.0 / (:rrf_k + s.rank), 0) +
           COALESCE(1.0 / (:rrf_k + k.rank), 0) AS rrf_score,
           COALESCE(s.similarity, 0) AS similarity
    FROM semantic s FULL OUTER JOIN keyword k ON s.id = k.id
)
```

**CTE 3 — `rrf`:** ה-`FULL OUTER JOIN` הוא הפרט הקריטי — הוא שומר תוצאות שהופיעו **רק** באחד משני החיפושים. `COALESCE(..., 0)` נותן 0 לצד החסר.

### 2.4 RRF — Reciprocal Rank Fusion

```text
score(doc) = Σ  1 / (k + rank_i(doc))
```

עם k=60, המשקל של מקום 1 הוא 1/61 = 0.0164, מקום 2 הוא 1/62 = 0.0161, וכן הלאה.

**למה RRF ולא נרמול וסכימת הציונים?**

זו השאלה החכמה בתחום. הבעיה: cosine similarity הוא בטווח [0,1] וה-weighted keyword score הוא מספר שלם שרירותי (0-8). הם **לא באותה יחידה**. כדי לחבר אותם צריך לנרמל, והנרמול תלוי בהתפלגות הציונים שמשתנה מכל שאילתה לשאילתה.

**RRF מתעלם מהציונים לגמרי ומשתמש רק בדירוג.** דירוג הוא ordinal — הוא לא צריך נרמול. זה הופך את השיטה ליציבה ולחסינה בפני scale mismatch.

**למה k=60?** זה הערך מהמאמר המקורי (Cormack et al. 2009) והפך לסטנדרט דה-פקטו. תפקידו: **לרסן את ההשפעה של מקומות ראשונים**. בלי k (כלומר k=0), מקום 1 היה שווה 1.0 ומקום 2 שווה 0.5 — פער עצום. עם k=60 הפער בין מקום 1 למקום 2 הוא זעיר, מה שאומר שמסמך שנמצא **בשתי הרשימות** במקום סביר מנצח מסמך שנמצא ראשון ברשימה אחת בלבד. זה בדיוק מה שרוצים מ-fusion.

**k גדול יותר** = שיטוח נוסף, יותר משקל להסכמה בין השיטות. **k קטן** = יותר משקל למקום הראשון.

### 2.5 המשקולות של מילות המפתח

```python
FIELD_WEIGHTS = {"role": 3, "tech": 2, "location": 1}
```

**הנימוק:** התאמת תפקיד היא האות החזק ביותר לרלוונטיות בשאלת שכר. טכנולוגיה חשובה אבל משנית (Backend עם Python או Go — השכר דומה). מיקום הוא האות החלש (יש עשרות אלפי אנשים בתל אביב).

**הודאה חשובה: המשקולות האלה לא נבדקו אמפירית.** בחרתי אותן מאינטואיציה. הדבר הנכון היה grid search על סט הבדיקה — למשל להריץ את ה-ablation עם (3,2,1) מול (5,2,1) מול (2,2,2) ולראות איזו קומבינציה נותנת MRR הכי גבוה. זו תשובה שמראה בגרות: להכיר במגבלה ולדעת איך היו בודקים.

### 2.6 אבטחה — הזרקת SQL

זו שאילתה **דינמית** — תנאי ה-`CASE WHEN` נבנים כמחרוזת ומשורשרים ל-SQL. זו קלאסיקה של SQL Injection.

```python
def _sanitize_keyword(kw: str) -> str:
    cleaned = re.sub(r"[^\w\s]", "", kw)   # רק אותיות, ספרות, קו תחתון ורווח
    return cleaned[:50].strip()
```

**מה זה מונע:** מסיר גרשיים, נקודה-פסיק, מקפים כפולים — כל התווים שמאפשרים לסגור מחרוזת ולהזריק פקודה. `\w` ב-Python 3 הוא Unicode-aware, כך שעברית עוברת. הקיצור ל-50 תווים מונע DoS דרך מחרוזות ענק.

**התשובה הכנה בראיון:** "זו הגנה שעובדת אבל היא לא הפתרון הנכון — allowlist טוב מ-denylist, אבל **פרמטריזציה** טובה משניהם. הפתרון הנכון: להעביר את מילות המפתח כמערך פרמטר ולהשתמש ב-`ANY(:keywords)` או ב-`unnest()`, כך שהמנוע מטפל בהן כדאטה ולא כקוד. זה ה-refactor שהייתי עושה."

**קונטקסט מרגיע:** מקור מילות המפתח הוא **פלט של GPT** בסכמה מוגבלת, לא קלט משתמש ישיר. זה מקטין את משטח התקיפה — אבל לא סוגר אותו (prompt injection יכול תיאורטית לגרום ל-GPT להחזיר מחרוזת זדונית, ולכן הסניטציה נחוצה).

### 2.7 מגבלה ידועה — שדה ה-`tech`

```python
f"CASE WHEN LOWER(role) LIKE '%{safe_kw}%' OR LOWER(company_stage) LIKE '%{safe_kw}%' ..."
```

מילות מפתח מסוג `tech` (למשל "kubernetes") מחופשות מול `role` ו-`company_stage`. אבל `company_stage` מכיל רק ערכים כמו "Startup"/"Series B" — **הוא לעולם לא יכיל שם טכנולוגיה**. אין בסכמה עמודת `tech`.

**המשמעות:** משקל ה-tech כמעט לא מייצר התאמות בפועל. זו מגבלה אמיתית שכדאי להכיר ולהציע לה תיקון: להוסיף עמודת `tech_stack` (מערך) שה-extractor ימלא, ולחפש בה — או לחפש ב-`raw_text` שבו הטכנולוגיות באמת מוזכרות.

---

## שלב 3 — Reranking (post-retrieval)

קובץ: `app/rag/reranker.py`

### למה בכלל צריך שלב נוסף

ה-retrieval מחזיר 10 מועמדים לפי ציון RRF. אבל דמיון וקטורי ≠ רלוונטיות אמיתית. "כמה מרוויח DevOps **בכיר**?" — הרטריבר יחזיר גם DevOps ג'וניור, כי הווקטור דומה. רק מודל שקורא את התוכן מבין שהניסיון לא מתאים.

**התובנה המבנית:** הרטריבר אופטימלי ל-**recall** (לא לפספס), הרירנקר אופטימלי ל-**precision** (לדייק). זו חלוקת עבודה מכוונת — מכניסים רשת רחבה (10) ומסננים לצרה (3).

### המימוש

GPT מקבל את 10 המועמדים בפורמט מובנה ומחזיר מערך של אינדקסים מסודר: `[3, 1, 7]`.

**החלטות:**
- מחזירים רק **אינדקסים**, לא טקסט — פלט של ~20 טוקנים במקום מאות. זול ומהיר.
- `max_tokens=50` — תקרה קשיחה.
- **דילוג על השלב** אם יש ≤2 מועמדים — אין מה לדרג, חוסך קריאה שלמה.
- **דדופליקציה** — `seen_ids` מונע כפילות אם GPT מחזיר את אותו אינדקס פעמיים.
- **ולידציית טווח** — `if 1 <= i <= len(posts)` מגן מפני הזיית אינדקס.

### Fallback — הדפוס החוזר בפרויקט

```python
except json.JSONDecodeError:
    return posts[:top_k]     # נופל חזרה לסדר של ה-RRF
except Exception:
    return posts[:top_k]
```

אם הרירנקר נכשל, המערכת מחזירה את 3 הראשונים לפי RRF. **המשתמש מקבל תשובה קצת פחות טובה, לא שגיאה.** זה עיקרון תכנוני שחוזר בכל הפרויקט: graceful degradation.

### למה LLM ולא Cross-Encoder

Cross-encoder הוא הסטנדרט התעשייתי ל-reranking (למשל `ms-marco-MiniLM`) — הוא מקודד את השאילתה והמסמך **יחד** ומחזיר ציון רלוונטיות. הוא מהיר יותר וזול יותר מ-LLM.

**למה לא בחרתי בו:** cross-encoders איכותיים לעברית כמעט לא קיימים. הם אומנו על MS MARCO באנגלית.

**מה החלופות שכן שקלתי:**
- **Cohere Rerank** — API מנוהל, תומך רב-לשונית. החלופה הכי אמיתית, מוסיף ספק חיצוני נוסף.
- **BGE-reranker-v2-m3** — רב-לשוני ופתוח. דורש הרצה מקומית.

**המחיר של הבחירה שלי:** LLM reranking הוא איטי יותר (קריאת רשת שלמה) ולא דטרמיניסטי לחלוטין. זה trade-off מודע: דיוק בעברית תמורת latency.

---

## שלב 4 — Generation

קובץ: `app/rag/generator.py` — האורקסטרטור.

### ה-System Prompt וההנדסה שבו

```text
You are an expert on the Israeli tech job market.
Answer salary questions based only on the real community data provided.

Rules:
- Only use the data provided. Never invent numbers.
- If there is not enough data — say so explicitly.
- Give a salary range, not a single number, when possible.
- Answer in Hebrew, clearly and directly.
- At the end, state how many posts you used.
```

כל שורה כאן היא **הגנה מפני מצב כשל ספציפי**:

| השורה | מפני מה היא מגנה |
|---|---|
| "based only on the data provided" | הזיות — המודל שולף מספר מהאימון |
| "Never invent numbers" | חיזוק מפורש של אותו כלל |
| "If there is not enough data — say so" | תשובה בטוחה בעצמה על בסיס מקורות חלשים |
| "Give a range, not a single number" | דיוק מדומה. 3 פוסטים לא מספיקים ל"38,500 ₪" |
| "Answer in Hebrew" | המודל נוטה לענות באנגלית כשה-context מעורב |
| "state how many posts you used" | שקיפות למשתמש |

**`temperature=0.3`** — לא 0 ולא 0.7. מספיק נמוך כדי לשמור על עקביות עובדתית, מספיק גבוה כדי שהעברית תזרום. שימו לב שזו הטמפרטורה **הגבוהה ביותר** בכל הצינור — בכל שאר השלבים היא 0, כי שם המשימה היא מבנית ולא לשונית.

### בניית ה-Context

```python
f"Post {i}:\n"
f"Role: {post['role']} | Experience: ... | Salary: ...₪ | Location: ...\n"
f"Quote: {post['raw_text']}\n"
```

נותנים למודל **גם** את המטא-דאטה המנורמל **וגם** את הציטוט הגולמי. המטא-דאטה קל לו לעבד ולהשוות; הציטוט נותן לו הקשר וניואנס (למשל "כולל בונוסים", "יומיים מהבית"). המספור `Post 1/2/3` מאפשר לו להתייחס למקורות.

### טיפול בשגיאות מדורג

```python
except RateLimitError:      → GenerationError("Server overloaded, please try again")
except APIConnectionError:  → GenerationError("AI server connection error")
```

**שני עקרונות:**
1. **תרגום שגיאות** — שגיאה טכנית של OpenAI הופכת להודעה שהמשתמש יכול להבין ולפעול לפיה.
2. **אין דליפת מידע** — ב-`routes.py` יש `except Exception` שמחזיר "Internal server error" גנרי ורושם את הפרטים ל-log בלבד. stack trace לא מגיע ללקוח לעולם.

**מיפוי קודי HTTP:**
- `400` — שאילתה ריקה
- `401` — API key שגוי
- `422` — פוסט שנכשל בולידציה ב-ingest
- `429` — חריגת rate limit
- `503` — `SalaryIntelError` (תלות חיצונית נפלה) — כלומר "נסה שוב"
- `500` — כל השאר, בלי פרטים

### מסלול "אין תוצאות"

```python
if not candidates:
    return {"answer": "לא נמצאו נתונים רלוונטיים לשאלה שלך.", "sources": [], "posts_used": 0}
```

**מוקדם ולפני ה-LLM.** אין טעם לשלם על קריאה ל-GPT כשאין context. וחשוב מכך — זה מונע מהמודל להמציא תשובה מהאוויר.

---

## שלב 5 — Observability

קובץ: `app/core/query_logger.py`

### QueryTracker

```python
with tracker.track_stage("retrieval"):
    candidates = await search_similar_posts(query, limit=10)
```

Context manager שמודד זמן ושומר אותו ב-`self.latency_retrieval` דרך `setattr`. שלושה שלבים נמדדים: `retrieval`, `reranking`, `generation`.

**למה context manager ולא `time.time()` ידני?** כי `finally` מבטיח שהמדידה נרשמת **גם אם השלב זרק חריגה**. שאילתות כושלות הן בדיוק אלה שמעניין לדעת כמה זמן לקחו.

### חישוב עלות

```python
COST_PER_INPUT_TOKEN  = 0.00000015   # $0.15 / 1M
COST_PER_OUTPUT_TOKEN = 0.0000006    # $0.60 / 1M

def add_tokens(self, input_tokens, output_tokens):
    self.tokens_used += input_tokens + output_tokens
    return round(input * COST_IN + output * COST_OUT, 6)
```

הטוקנים נלקחים מ-`response.usage` — נתון אמיתי מ-OpenAI, לא הערכה.

**מגבלה שכדאי להודות בה:** נספרים רק הטוקנים של ה-**generation**. ה-expansion, ה-reranking וה-embedding לא נספרים. העלות האמיתית לשאילתה גבוהה ממה שהמערכת מדווחת (בערך פי 2-3). זה תיקון קל ושווה לציין אותו.

### טבלת `query_logs`

כל שאילתה נשמרת עם: השאילתה עצמה, latency לכל שלב + total, כמה פוסטים נשלפו ואילו IDs, טוקנים, עלות, סטטוס הצלחה והודעת שגיאה.

**מה זה מאפשר:**
```sql
-- מי איטי?
SELECT query, latency_total FROM query_logs ORDER BY latency_total DESC LIMIT 10;

-- כמה זה עולה לי ביום?
SELECT DATE(created_at), COUNT(*), SUM(estimated_cost_usd) FROM query_logs GROUP BY 1;

-- אילו שאילתות לא מחזירות כלום? (פערי דאטה!)
SELECT query FROM query_logs WHERE posts_retrieved = 0;

-- אחוז כשלונות
SELECT success, COUNT(*) FROM query_logs GROUP BY success;
```

השאילתה השלישית היא הכי מעניינת — היא מייצרת **רשימת קניות של דאטה חסר**. שאילתות שלא מחזירות תוצאות מראות בדיוק אילו תפקידים או אזורים חסרים במסד.

**המשפט לראיון:** "בניתי את ה-logging *לפני* שידעתי מה הבעיה. אחר כך ה-logging הוא זה שהראה לי שהבעיה היא ב-retrieval, וזה הוביל לאופטימיזציית ה-async שנתנה 62%. מדידה קודמת לאופטימיזציה."
