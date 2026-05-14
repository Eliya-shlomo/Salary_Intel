import sys
sys.path.append(".")

from app.rag.evaluator import evaluate_retrieval
from app.rag.test_cases import TEST_CASES

if __name__ == "__main__":
    print("\n🔍 מריץ Retrieval Evaluation...\n")
    metrics = evaluate_retrieval(TEST_CASES, k=3)

    print(f"\n📊 תוצאות סופיות:")
    print(f"   Hit Rate@3: {metrics['hit_rate_at_k']}")
    print(f"   MRR:        {metrics['mrr']}")
    print(f"   NDCG@3:     {metrics['ndcg_at_k']}")
