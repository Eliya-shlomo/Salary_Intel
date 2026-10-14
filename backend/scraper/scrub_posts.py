"""Remove people's names from collected posts before they are sent anywhere.

The PrivacyAgent only proposes substrings to remove. The code checks that every substring
really exists in the post and replaces it with [name]. When the agent proposes something
that is not in the post, the post goes to the unsure file instead of the clean one.

    PYTHONPATH=. .venv/bin/python -m scraper.scrub_posts scraper/output/posts_X.jsonl

Writes posts_X.clean.jsonl (ready for send_posts) and posts_X.unsure.jsonl (review by hand).
"""
import argparse
import asyncio
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from scraper.filters import redact
from scraper.privacy_agent import review_post

NAME_TOKEN = "[name]"
MAX_SPAN_CHARS = 40
DERIVED_SUFFIXES = (".clean.jsonl", ".unsure.jsonl", ".results.jsonl")


@dataclass
class ScrubbedPost:
    text: str
    decision: str
    removed: list[str] = field(default_factory=list)
    problems: list[str] = field(default_factory=list)
    reason: str = ""


def apply_spans(text: str, spans: list[str]) -> tuple[str, list[str], list[str]]:
    """Replace verified spans with [name]. Returns (text, removed, problems)."""
    removed, problems = [], []
    for span in sorted({s.strip() for s in spans if s.strip()}, key=len, reverse=True):
        if len(span) > MAX_SPAN_CHARS:
            problems.append(f"span too long to be a name: {span[:20]}...")
        elif span not in text:
            problems.append(f"span not found in post: {span}")
        else:
            removed.append(span)
    for span in removed:
        text = text.replace(span, NAME_TOKEN)
    return text, removed, problems


async def scrub_post(text: str) -> ScrubbedPost:
    text = redact(text)
    review = await review_post(text)
    clean_text, removed, problems = apply_spans(text, review.spans)
    decision = review.decision
    if decision == "keep" and problems:
        decision = "unsure"
    return ScrubbedPost(clean_text, decision, removed, problems, review.reason)


def output_paths(path: Path) -> tuple[Path, Path]:
    stem = path.name.removesuffix(".jsonl")
    return path.with_name(f"{stem}.clean.jsonl"), path.with_name(f"{stem}.unsure.jsonl")


async def scrub_file(path: Path) -> tuple[Counter, list[ScrubbedPost]]:
    if not path.name.endswith(".jsonl") or path.name.endswith(DERIVED_SUFFIXES):
        raise ValueError(f"Expected a raw posts_X.jsonl file from collect_facebook, got {path.name}")

    posts = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    scrubbed = [await scrub_post(post["text"]) for post in posts]

    clean_path, unsure_path = output_paths(path)
    lines = {"keep": [], "unsure": []}
    for post, result in zip(posts, scrubbed):
        if result.decision in lines:
            record = {"text": result.text, "source": post.get("source", "facebook_group")}
            lines[result.decision].append(json.dumps(record, ensure_ascii=False) + "\n")
    clean_path.write_text("".join(lines["keep"]))
    if lines["unsure"]:
        unsure_path.write_text("".join(lines["unsure"]))
    return Counter(result.decision for result in scrubbed), scrubbed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("file", type=Path)
    args = parser.parse_args()

    try:
        counts, scrubbed = asyncio.run(scrub_file(args.file))
    except ValueError as error:
        print(error)
        return 2

    for index, result in enumerate(scrubbed, 1):
        removed = ", ".join(result.removed) or "-"
        print(f"[{index}] {result.decision:6}  removed: {removed}")
        for problem in result.problems:
            print(f"        problem: {problem}")
        if result.decision != "keep":
            print(f"        reason: {result.reason}")
    print(dict(counts))

    clean_path, unsure_path = output_paths(args.file)
    print(f"Review {clean_path} before sending.")
    if counts.get("unsure"):
        print(f"Edit {unsure_path} by hand; move safe lines into the clean file.")
    print(f"Next: PYTHONPATH=. .venv/bin/python -m scraper.send_posts {clean_path} --delete-after-send")
    return 0


if __name__ == "__main__":
    sys.exit(main())
