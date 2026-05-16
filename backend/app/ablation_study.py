import asyncio
import sys
sys.path.append(".")

from app.rag.evaluator import hit_rate_at_k, reciprocal_rank, ndcg_at_k
from app.rag.embeddings import get_embedding
from app.rag.query_parser import expand_query
from app.rag.reranker import rerank_results
from app.db.database import SessionLocal
from sqlalchemy import text
import json

# Load generated test cases instead of manual ones
with open("app/generated_test_cases.json", "r", encoding="utf-8") as f:
    TEST_CASES = json.load(f)

K = 3
THRESHOLD = 0.25
RRF_K = 60


# ── Version 1: Semantic only ──────────────────────────────────────────────────

async def search_semantic_only(query: str, limit: int) -> list[dict]:
    embedding = await get_embedding(query)
    db = SessionLocal()
    try:
        results = db.execute(text("""
            SELECT id, role, salary, years_experience, location,
                   1 - (embedding <=> CAST(:emb AS vector)) AS similarity
            FROM salary_posts
            WHERE 1 - (embedding <=> CAST(:emb AS vector)) > :threshold
            ORDER BY embedding <=> CAST(:emb AS vector)
            LIMIT :limit
        """), {"emb": str(embedding), "threshold": THRESHOLD, "limit": limit}).fetchall()

        return [{"id": r.id, "role": r.role, "salary": r.salary,
                 "years_experience": r.years_experience, "location": r.location,
                 "similarity": round(r.similarity, 3)} for r in results]
    finally:
        db.close()


# ── Version 2: Hybrid (no expansion) ─────────────────────────────────────────

async def search_hybrid_no_expansion(query: str, limit: int) -> list[dict]:
    embedding = await get_embedding(query)

    # Simple keyword: search the query directly on role/location
    db = SessionLocal()
    try:
        results = db.execute(text(f"""
            WITH semantic AS (
                SELECT id,
                       1 - (embedding <=> CAST(:emb AS vector)) AS similarity,
                       ROW_NUMBER() OVER (ORDER BY embedding <=> CAST(:emb AS vector)) AS rank
                FROM salary_posts
                WHERE 1 - (embedding <=> CAST(:emb AS vector)) > :threshold
            ),
            keyword AS (
                SELECT id,
                       ROW_NUMBER() OVER (ORDER BY match_score DESC) AS rank
                FROM (
                    SELECT id,
                           CASE WHEN LOWER(role) LIKE :pattern THEN 3 ELSE 0 END +
                           CASE WHEN LOWER(location) LIKE :pattern THEN 1 ELSE 0 END AS match_score
                    FROM salary_posts
                    WHERE LOWER(role) LIKE :pattern OR LOWER(location) LIKE :pattern
                ) scored WHERE match_score > 0
            ),
            rrf AS (
                SELECT COALESCE(s.id, k.id) AS id,
                       COALESCE(1.0/(:rrf_k+s.rank),0) + COALESCE(1.0/(:rrf_k+k.rank),0) AS rrf_score,
                       COALESCE(s.similarity,0) AS similarity
                FROM semantic s FULL OUTER JOIN keyword k ON s.id=k.id
            )
            SELECT p.id, p.role, p.salary, p.years_experience, p.location,
                   r.similarity, r.rrf_score
            FROM rrf r JOIN salary_posts p ON p.id=r.id
            ORDER BY r.rrf_score DESC LIMIT :limit
        """), {
            "emb": str(embedding),
            "threshold": THRESHOLD,
            "rrf_k": RRF_K,
            "pattern": f"%{query.lower()[:20]}%",
            "limit": limit
        }).fetchall()

        return [{"id": r.id, "role": r.role, "salary": r.salary,
                 "years_experience": r.years_experience, "location": r.location,
                 "similarity": round(r.similarity, 3)} for r in results]
    finally:
        db.close()


# ── Version 3: Hybrid + Query Expansion (no reranking) ───────────────────────

async def search_hybrid_with_expansion(query: str, limit: int) -> list[dict]:
    from app.rag.retriever import search_similar_posts
    return await search_similar_posts(query, limit=limit)


# ── Version 4: Full pipeline ──────────────────────────────────────────────────

async def search_full_pipeline(query: str, limit: int) -> list[dict]:
    from app.rag.retriever import search_similar_posts
    candidates = await search_similar_posts(query, limit=limit)
    return await rerank_results(query, candidates, top_k=K)


# ── Evaluation runner ─────────────────────────────────────────────────────────

async def evaluate_version(name: str, search_fn, limit: int = 10) -> dict:
    print(f"\n{'─'*50}")
    print(f"Version: {name}")
    print('─'*50)

    hit_rates, mrr_scores, ndcg_scores = [], [], []

    for case in TEST_CASES:
        results = await search_fn(case["query"], limit)
        hr   = hit_rate_at_k(results, case["relevant_ids"], K)
        rr   = reciprocal_rank(results, case["relevant_ids"])
        ndcg = ndcg_at_k(results, case["relevant_ids"], K)

        hit_rates.append(hr)
        mrr_scores.append(rr)
        ndcg_scores.append(ndcg)

        status = "✓" if hr == 1.0 else "✗"
        print(f"  {status} '{case['query'][:40]}' | HR={hr:.1f} MRR={rr:.2f} NDCG={ndcg:.2f}")

    metrics = {
        "name": name,
        "hit_rate": round(sum(hit_rates) / len(hit_rates), 3),
        "mrr":      round(sum(mrr_scores) / len(mrr_scores), 3),
        "ndcg":     round(sum(ndcg_scores) / len(ndcg_scores), 3),
    }

    print(f"\n  Hit Rate@{K}: {metrics['hit_rate']}")
    print(f"  MRR:         {metrics['mrr']}")
    print(f"  NDCG@{K}:    {metrics['ndcg']}")

    return metrics


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print("\n🔬 Ablation Study — Salary Intel RAG Pipeline")
    print("=" * 50)

    versions = [
        ("1. Semantic Only",                    search_semantic_only),
        ("2. Hybrid (no expansion)",             search_hybrid_no_expansion),
        ("3. Hybrid + Query Expansion",          search_hybrid_with_expansion),
        ("4. Full Pipeline (+ Reranking)",       search_full_pipeline),
    ]

    all_metrics = []
    for name, fn in versions:
        metrics = await evaluate_version(name, fn)
        all_metrics.append(metrics)

    # Summary table
    print(f"\n\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"{'Version':<40} {'Hit Rate':>10} {'MRR':>8} {'NDCG':>8}")
    print(f"{'─'*60}")
    for m in all_metrics:
        print(f"{m['name']:<40} {m['hit_rate']:>10} {m['mrr']:>8} {m['ndcg']:>8}")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())