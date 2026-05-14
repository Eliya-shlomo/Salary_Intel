from app.ingestion.ingestor import ingest_post
from app.core.logging import get_logger

logger = get_logger(__name__)


def bulk_ingest(posts: list[str], source: str = "facebook") -> dict:
    """
    מכניס רשימת פוסטים גולמיים עם חילוץ אוטומטי.

    מחזיר סיכום: כמה הצליחו, כמה נכשלו, כמה לא רלוונטיים.
    """
    results = {
        "success": 0,
        "skipped": 0,
        "failed": 0,
        "total": len(posts),
    }

    for i, raw_text in enumerate(posts, 1):
        logger.info(f"[{i}/{len(posts)}] מעבד פוסט...")

        try:
            ingest_post(
                raw_text=raw_text,
                source=source,
                auto_extract=True,
            )
            results["success"] += 1

        except ValueError as e:
            # פוסט לא רלוונטי — לא שגיאה
            logger.info(f"דולג: {e}")
            results["skipped"] += 1

        except Exception as e:
            logger.error(f"נכשל: {e}")
            results["failed"] += 1

    logger.info(
        f"\nסיכום: {results['success']} הצליחו | "
        f"{results['skipped']} דולגו | "
        f"{results['failed']} נכשלו"
    )

    return results