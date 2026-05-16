from app.ingestion.ingestor import ingest_post
from app.core.logging import get_logger

logger = get_logger(__name__)


async def bulk_ingest(posts: list[str], source: str = "facebook") -> dict:
    """
    Ingests a list of raw posts with automatic metadata extraction.
    """
    results = {
        "success": 0,
        "skipped": 0,
        "failed": 0,
        "total": len(posts),
    }

    for i, raw_text in enumerate(posts, 1):
        logger.info(f"[{i}/{len(posts)}] Processing post...")

        try:
            await ingest_post(
                raw_text=raw_text,
                source=source,
                auto_extract=True,
            )
            results["success"] += 1

        except ValueError as e:
            logger.info(f"Skipped: {e}")
            results["skipped"] += 1

        except Exception as e:
            logger.error(f"Failed: {e}")
            results["failed"] += 1

    logger.info(
        f"\nSummary: {results['success']} succeeded | "
        f"{results['skipped']} skipped | "
        f"{results['failed']} failed"
    )

    return results