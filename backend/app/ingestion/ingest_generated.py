"""Ingest a generated dataset through the same pipeline as POST /posts.

Posts go one at a time, because duplicate detection must see the posts
saved before it. Each outcome is written next to the dataset with the
generated id, so extraction can later be scored against ground_truth.jsonl.

    python -m app.ingestion.ingest_generated data/synthetic_v2
"""
import asyncio
import json
import sys
from collections import Counter
from pathlib import Path

from app.db.database import SessionLocal
from app.ingestion.orchestrator import ingest_pipeline


async def ingest_dataset(data_dir: Path, ingest=ingest_pipeline, session_factory=SessionLocal) -> Counter:
    posts = [
        json.loads(line)
        for line in (data_dir / "posts.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    results_path = data_dir / "ingest_results.jsonl"
    done = set()
    if results_path.exists():
        done = {json.loads(line)["id"] for line in results_path.read_text().splitlines()}

    counts: Counter = Counter()
    with open(results_path, "a", encoding="utf-8") as results:
        for i, post in enumerate(posts, 1):
            if post["id"] in done:
                continue
            db = session_factory()
            try:
                outcome = await ingest(db, post["raw_text"], source=post["source"])
                db.commit()
                status = outcome.status
                row = {"id": post["id"], **outcome.model_dump()}
            except ValueError as error:
                db.rollback()
                status = "rejected"
                row = {"id": post["id"], "status": status, "error": str(error)}
            except Exception as error:
                db.rollback()
                status = "error"
                row = {"id": post["id"], "status": status, "error": type(error).__name__}
            finally:
                db.close()
            if status != "error":
                results.write(json.dumps(row, ensure_ascii=False) + "\n")
                results.flush()
            counts[status] += 1
            print(f"[{i}/{len(posts)}] {post['id']} {status}", flush=True)
    return counts


def main() -> None:
    counts = asyncio.run(ingest_dataset(Path(sys.argv[1])))
    print(dict(counts))


if __name__ == "__main__":
    main()
