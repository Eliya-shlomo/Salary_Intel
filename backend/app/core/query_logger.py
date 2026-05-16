import time
from contextlib import contextmanager
from app.db.database import SessionLocal
from app.db.models import QueryLog
from app.core.logging import get_logger

logger = get_logger(__name__)

# GPT-4o-mini pricing (per 1M tokens)
COST_PER_INPUT_TOKEN = 0.00000015   # $0.15 per 1M
COST_PER_OUTPUT_TOKEN = 0.0000006   # $0.60 per 1M


class QueryTracker:
    """
    Tracks latency and cost for a single query across all pipeline stages.
    Usage: create once per query, call start/end for each stage.
    """

    def __init__(self, query: str):
        self.query = query
        self.start_time = time.time()

        self.latency_retrieval: float | None = None
        self.latency_reranking: float | None = None
        self.latency_generation: float | None = None

        self.posts_retrieved: int = 0
        self.posts_after_rerank: int = 0
        self.retrieved_post_ids: list[int] = []

        self.tokens_used: int = 0
        self.success: bool = True
        self.error_message: str | None = None

    @contextmanager
    def track_stage(self, stage: str):
        """Context manager to track latency of a single stage."""
        t = time.time()
        try:
            yield
        finally:
            elapsed = round(time.time() - t, 3)
            setattr(self, f"latency_{stage}", elapsed)
            logger.info(f"Stage '{stage}' completed in {elapsed}s")

    def add_tokens(self, input_tokens: int, output_tokens: int):
        """Track token usage and estimate cost."""
        self.tokens_used += input_tokens + output_tokens
        cost = (input_tokens * COST_PER_INPUT_TOKEN) + (output_tokens * COST_PER_OUTPUT_TOKEN)
        return round(cost, 6)

    def save(self, estimated_cost_usd: float = 0.0):
        """Save the completed query log to the database."""
        total = round(time.time() - self.start_time, 3)

        db = SessionLocal()
        try:
            log = QueryLog(
                query=self.query,
                latency_retrieval=self.latency_retrieval,
                latency_reranking=self.latency_reranking,
                latency_generation=self.latency_generation,
                latency_total=total,
                posts_retrieved=self.posts_retrieved,
                posts_after_rerank=self.posts_after_rerank,
                retrieved_post_ids=self.retrieved_post_ids,
                tokens_used=self.tokens_used,
                estimated_cost_usd=estimated_cost_usd,
                success=self.success,
                error_message=self.error_message,
            )
            db.add(log)
            db.commit()
            logger.info(
                f"Query logged | total={total}s | "
                f"tokens={self.tokens_used} | "
                f"cost=${estimated_cost_usd}"
            )
        except Exception as e:
            logger.error(f"Failed to save query log: {e}")
        finally:
            db.close()