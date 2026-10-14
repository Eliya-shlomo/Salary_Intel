"""Score the ingestion pipeline against the facts each generated post was built from.

Reads ground_truth.jsonl and ingest_results.jsonl from a dataset folder,
loads the saved rows, and compares field by field. Duplicates are left out.

    PYTHONPATH=. .venv/bin/python -m evals.extraction_accuracy data/synthetic_v2
"""
import json
import sys
from collections import Counter
from pathlib import Path

from app.db.database import SessionLocal
from app.db.models import SalaryPost

FIELDS = ("role", "salary", "pay_basis", "has_equity", "years_experience")


def _read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def field_matches(truth: dict, row: dict) -> dict[str, bool]:
    return {
        "role": row["role"] == truth["role"],
        "salary": row["salary_min"] == truth["salary"] and row["salary_max"] == truth["salary"],
        "pay_basis": row["pay_basis"] == truth["pay_basis"],
        "has_equity": bool(row["has_equity"]) == truth["has_equity"],
        "years_experience": row["years_experience"] == truth["years_experience"],
    }


def score(truth: list[dict], results: list[dict], rows: dict[int, dict]) -> dict:
    by_id = {t["id"]: t for t in truth}
    outcome = Counter()
    correct = Counter()
    scored = 0
    misses: list[dict] = []

    for result in results:
        t = by_id[result["id"]]
        status = result["status"]
        if status == "duplicate":
            outcome["duplicate"] += 1
            continue
        if not t["is_salary_post"]:
            outcome["question rejected" if status == "rejected" else "question admitted"] += 1
            continue
        if status == "rejected":
            outcome["salary post rejected"] += 1
            continue
        outcome[f"salary post {status}"] += 1
        matches = field_matches(t, rows[result["post_id"]])
        scored += 1
        correct.update(name for name, ok in matches.items() if ok)
        wrong = [name for name, ok in matches.items() if not ok]
        if wrong:
            misses.append({"id": t["id"], "wrong": wrong})

    return {
        "outcomes": dict(outcome),
        "scored": scored,
        "accuracy": {f: correct[f] / scored if scored else None for f in FIELDS},
        "all_fields_correct": (scored - len(misses)) / scored if scored else None,
        "misses": misses,
    }


def load_rows(post_ids: list[int]) -> dict[int, dict]:
    db = SessionLocal()
    try:
        posts = db.query(SalaryPost).filter(SalaryPost.id.in_(post_ids)).all()
        return {
            p.id: {
                "role": p.role_canonical,
                "salary_min": p.salary_min,
                "salary_max": p.salary_max,
                "pay_basis": p.pay_basis,
                "has_equity": p.has_equity,
                "years_experience": p.years_experience,
            }
            for p in posts
        }
    finally:
        db.close()


def main() -> None:
    data_dir = Path(sys.argv[1])
    truth = _read_jsonl(data_dir / "ground_truth.jsonl")
    results = _read_jsonl(data_dir / "ingest_results.jsonl")
    rows = load_rows([r["post_id"] for r in results if r.get("post_id")])
    report = score(truth, results, rows)

    out = Path(__file__).parent / "results" / "extraction_accuracy.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(json.dumps({k: v for k, v in report.items() if k != "misses"}, indent=2, ensure_ascii=False))
    print(f"{len(report['misses'])} posts with at least one wrong field; details in {out}")


if __name__ == "__main__":
    main()
