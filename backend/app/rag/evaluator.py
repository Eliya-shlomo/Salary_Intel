import math
from app.rag.retriever import search_similar_posts
from app.core.logging import get_logger

logger = get_logger(__name__)


def hit_rate_at_k(results: list[dict], relevant_ids: list[int], k: int) -> float:
    """
    האם לפחות אחת מה-relevant_ids הופיעה בtop-k תוצאות?
    מחזיר 1.0 או 0.0
    """
    top_k_ids = [r["id"] for r in results[:k]]
    return 1.0 if any(rid in top_k_ids for rid in relevant_ids) else 0.0


def reciprocal_rank(results: list[dict], relevant_ids: list[int]) -> float:
    """
    1/rank של התוצאה הרלוונטית הראשונה.
    אם לא נמצאה — 0.
    """
    for i, result in enumerate(results, 1):
        if result["id"] in relevant_ids:
            return 1.0 / i
    return 0.0


def ndcg_at_k(results: list[dict], relevant_ids: list[int], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain.
    מתחשב בדירוג של כל התוצאות הרלוונטיות.
    """
    def dcg(hits: list[int]) -> float:
        return sum(
            hit / math.log2(i + 2)
            for i, hit in enumerate(hits[:k])
        )

    # DCG של התוצאות שלנו
    hits = [1 if r["id"] in relevant_ids else 0 for r in results[:k]]
    actual_dcg = dcg(hits)

    # DCG אידיאלי — כל הרלוונטיים ראשונים
    ideal_hits = sorted(hits, reverse=True)
    ideal_dcg = dcg(ideal_hits)

    if ideal_dcg == 0:
        return 0.0

    return actual_dcg / ideal_dcg


def evaluate_retrieval(test_cases: list[dict], k: int = 3) -> dict:
    """
    מריץ evaluation על רשימת test cases.

    כל test case:
    {
        "query": "כמה מרוויח DevOps?",
        "relevant_ids": [2]  ← IDs של פוסטים רלוונטיים
    }
    """
    hit_rates = []
    mrr_scores = []
    ndcg_scores = []

    logger.info(f"מריץ evaluation על {len(test_cases)} שאלות...")

    for i, case in enumerate(test_cases, 1):
        query = case["query"]
        relevant_ids = case["relevant_ids"]

        results = search_similar_posts(query, limit=k)

        hr = hit_rate_at_k(results, relevant_ids, k)
        rr = reciprocal_rank(results, relevant_ids)
        ndcg = ndcg_at_k(results, relevant_ids, k)

        hit_rates.append(hr)
        mrr_scores.append(rr)
        ndcg_scores.append(ndcg)

        status = "✓" if hr == 1.0 else "✗"
        logger.info(
            f"  [{i}] {status} '{query[:40]}' | "
            f"HR={hr:.1f} MRR={rr:.2f} NDCG={ndcg:.2f}"
        )

    metrics = {
        "hit_rate_at_k": round(sum(hit_rates) / len(hit_rates), 3),
        "mrr": round(sum(mrr_scores) / len(mrr_scores), 3),
        "ndcg_at_k": round(sum(ndcg_scores) / len(ndcg_scores), 3),
        "k": k,
        "total_queries": len(test_cases),
    }

    logger.info(f"\n{'='*50}")
    logger.info(f"Hit Rate@{k}: {metrics['hit_rate_at_k']}")
    logger.info(f"MRR:         {metrics['mrr']}")
    logger.info(f"NDCG@{k}:    {metrics['ndcg_at_k']}")
    logger.info(f"{'='*50}")

    return metrics
