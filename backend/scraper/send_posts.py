"""Send scrubbed posts to the ingestion pipeline (POST /api/v1/posts).

Only accepts files that went through scrub_posts (*.clean.jsonl). The endpoint allows
5 requests per minute, so posts are sent one every 13 seconds. Every outcome is written
to a results file next to the input, so a stopped run can be resumed without sending
any post twice.

    PYTHONPATH=. .venv/bin/python -m scraper.send_posts scraper/output/posts_X.clean.jsonl
"""
import argparse
import json
import sys
import time
from collections import Counter
from collections.abc import Callable
from pathlib import Path

import httpx

from app.core.config import settings
from scraper.filters import fingerprint

DEFAULT_API_URL = "http://localhost:8000"
CLEAN_SUFFIX = ".clean.jsonl"
SECONDS_BETWEEN_POSTS = 13
RATE_LIMIT_WAIT_SECONDS = 65
STATUS_LABELS = {
    201: "approved",
    202: "pending_review",
    409: "duplicate",
    422: "not_a_salary_post",
}
FINAL_OUTCOMES = set(STATUS_LABELS.values())


def results_path(path: Path) -> Path:
    return path.with_name(path.name.removesuffix(CLEAN_SUFFIX) + ".results.jsonl")


def raw_path(path: Path) -> Path:
    return path.with_name(path.name.removesuffix(CLEAN_SUFFIX) + ".jsonl")


def load_finished(path: Path) -> set[str]:
    if not path.exists():
        return set()
    finished = set()
    for line in path.read_text().splitlines():
        if line.strip():
            record = json.loads(line)
            if record["outcome"] in FINAL_OUTCOMES:
                finished.add(record["fingerprint"])
    return finished


def send_one(client: httpx.Client, url: str, post: dict, sleep: Callable[[float], None]) -> str:
    body = {"raw_text": post["text"], "source": post.get("source", "facebook_group")}
    for attempt in range(2):
        response = client.post(url, json=body)
        if response.status_code == 429 and attempt == 0:
            sleep(RATE_LIMIT_WAIT_SECONDS)
            continue
        return STATUS_LABELS.get(response.status_code, f"error_{response.status_code}")
    return "error_429"


def send_file(
    path: Path,
    api_url: str,
    client: httpx.Client | None = None,
    pause: float = SECONDS_BETWEEN_POSTS,
    sleep: Callable[[float], None] = time.sleep,
) -> Counter:
    if not path.name.endswith(CLEAN_SUFFIX):
        raise ValueError(f"Refusing to send {path.name}: run scrub_posts first and send the {CLEAN_SUFFIX} file")

    posts = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    log_path = results_path(path)
    finished = load_finished(log_path)
    owns_client = client is None
    client = client or httpx.Client(headers={"X-API-Key": settings.api_key}, timeout=120)
    url = f"{api_url}/api/v1/posts"
    results: Counter = Counter()
    sent_any = False
    try:
        with log_path.open("a") as log:
            for index, post in enumerate(posts, 1):
                key = fingerprint(post["text"])
                if key in finished:
                    results["already_sent"] += 1
                    continue
                if sent_any:
                    sleep(pause)
                outcome = send_one(client, url, post, sleep)
                sent_any = True
                log.write(json.dumps({"fingerprint": key, "outcome": outcome}) + "\n")
                log.flush()
                if outcome in FINAL_OUTCOMES:
                    finished.add(key)
                results[outcome] += 1
                print(f"[{index}/{len(posts)}] {outcome}")
    finally:
        if owns_client:
            client.close()
    return results


def delete_files(path: Path) -> list[Path]:
    deleted = []
    for candidate in (path, results_path(path), raw_path(path)):
        if candidate.exists():
            candidate.unlink()
            deleted.append(candidate)
    return deleted


def all_finished(path: Path) -> bool:
    posts = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    finished = load_finished(results_path(path))
    return all(fingerprint(post["text"]) in finished for post in posts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("file", type=Path)
    parser.add_argument("--api-url", default=DEFAULT_API_URL)
    parser.add_argument(
        "--delete-after-send",
        action="store_true",
        help="delete the clean, raw and results files once every post has a final outcome",
    )
    args = parser.parse_args()

    try:
        results = send_file(args.file, args.api_url)
    except ValueError as error:
        print(error)
        return 2
    except httpx.TransportError as error:
        print(f"Could not reach {args.api_url} ({error}). Run the same command again to resume.")
        return 1
    print(dict(results))

    if not all_finished(args.file):
        print("Some posts failed. Run the same command again to retry them.")
        return 1
    if args.delete_after_send:
        for deleted in delete_files(args.file):
            print(f"Deleted {deleted}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
