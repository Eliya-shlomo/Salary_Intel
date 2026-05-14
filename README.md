````md
# 🔍 Salary Intel — Hebrew AI Salary Intelligence Platform

> RAG-powered salary insights from real Israeli tech community discussions

## What is this?

A production-grade RAG system that answers Hebrew salary questions based on real data from Israeli tech communities.

Instead of hallucinating numbers, the system retrieves actual salary posts and generates grounded answers with sources.

**Example:**

```text
Query:  "כמה מרוויח DevOps בכיר בתל אביב?"
Answer: "לפי 3 דיונים אמיתיים מהקהילה, DevOps עם 6+ שנים מרוויח 42,000-55,000₪..."
Sources: [post_1, post_2, post_3]
````

---

## Architecture

```text
User Query
    ↓
LLM Query Expansion     (GPT extracts role/tech/location keywords)
    ↓
Hybrid Search           (Semantic + Weighted Keyword Search)
    ↓
RRF Fusion              (Reciprocal Rank Fusion merges results)
    ↓
Reranking               (GPT selects top 3 most relevant)
    ↓
Generation              (GPT answers based on evidence only)
    ↓
Grounded Answer + Sources
```

### Tech Stack

| Layer          | Technology                     | Why                                |
| -------------- | ------------------------------ | ---------------------------------- |
| API            | FastAPI                        | Async, auto docs, production-ready |
| Database       | PostgreSQL + pgvector          | Vector search without extra infra  |
| Embeddings     | OpenAI text-embedding-3-small  | Multilingual, cost-effective       |
| LLM            | GPT-4o-mini                    | Fast, cheap, Hebrew support        |
| Search         | Hybrid (Semantic + BM25-style) | Better recall than either alone    |
| Reranking      | LLM-based                      | No cross-encoder needed for Hebrew |
| Infrastructure | Docker Compose                 | One-command setup                  |

---

## Key Technical Decisions

### Why RAG over Fine-tuning?

Salary data changes constantly. RAG allows real-time updates without retraining. Fine-tuning would require expensive retraining for every new data point.

### Why Hybrid Search?

Semantic search alone misses exact tech keywords ("Kubernetes", "React").
Keyword search alone misses synonyms ("מהנדס תשתיות" ≠ "DevOps").
Hybrid with RRF fusion outperforms either approach.

### Why LLM Reranking over Cross-Encoder?

Hebrew cross-encoder models are limited. GPT-4o-mini understands Hebrew context deeply and reranks with high accuracy at low cost.

### Why pgvector over Pinecone/Weaviate?

Keeps the stack simple — one database for both relational data and vector search. Easier to maintain, lower operational cost for this scale.

---

## Getting Started

### Prerequisites

* Docker + Docker Compose
* OpenAI API key

### Run

```bash
# Clone
git clone https://github.com/your-username/salary-intel
cd salary-intel

# Set your OpenAI key
echo "OPENAI_API_KEY=sk-..." > .env

# Start everything
docker-compose up --build

# Initialize DB (first time only)
docker exec salary_intel_api python -m app.db.init_db
docker exec salary_intel_api python seed_data.py
```

### API

Swagger docs: `http://localhost:8000/docs`

#### Query endpoint

```bash
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "כמה מרוויח מפתח React עם 4 שנים?"}'
```

#### Response

```json
{
  "answer": "לפי הנתונים...",
  "posts_used": 3,
  "sources": [...]
}
```

---

## Project Structure

```text
salary-intel/
├── backend/
│   ├── app/
│   │   ├── api/          # FastAPI routes
│   │   ├── core/         # Config, logging, exceptions
│   │   ├── db/           # Models, database connection
│   │   ├── ingestion/    # Data ingestion pipeline
│   │   └── rag/          # Embeddings, retrieval, reranking, generation
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```

---

## RAG Pipeline Details

### 1. Query Expansion

Before searching, GPT extracts structured keywords:

```json
{
  "role": ["DevOps Engineer", "Senior DevOps"],
  "tech": ["AWS", "Kubernetes", "Docker"],
  "location": []
}
```

### 2. Hybrid Search + RRF

Two parallel searches merged via Reciprocal Rank Fusion:

```text
score = 1/(60 + rank_semantic) + 1/(60 + rank_keyword)
```

Posts appearing high in both searches get boosted scores.

### 3. Weighted Keyword Matching

Fields weighted by relevance to salary:

* `role` match → 3 points
* `tech` match → 2 points
* `location` match → 0.7 point

### 4. Security

SQL Injection protection on all dynamic queries:

```python
def _sanitize_keyword(kw: str) -> str:
    return re.sub(r"[^\w\s]", "", kw)[:50]
```

---

## Roadmap

* [ ] Real data ingestion from public sources
* [ ] Retrieval evaluation (MRR, Hit Rate)
* [ ] Next.js frontend
* [ ] User authentication
* [ ] Salary trend analysis over time

---
