"""Compare a generated dataset with the reference table it was sampled from.

For every role x bucket cell: the generated median against the reference
median. A cell is flagged when they differ by more than TOLERANCE, and
reported as "few" when it holds fewer than MIN_POSTS salary posts.

    PYTHONPATH=. .venv/bin/python -m evals.generated_sanity data/synthetic_v2
"""
import json
import sys
from pathlib import Path
from statistics import median

from app.ingestion.salary_reference import SalaryReference, load_reference

TOLERANCE = 0.10
MIN_POSTS = 5


def check(truth: list[dict], reference: SalaryReference) -> list[dict]:
    rows = []
    for cell in reference.cells:
        salaries = [
            t["salary"]
            for t in truth
            if t["role"] == cell.role and t["bucket"] == cell.bucket and t["salary"]
        ]
        if len(salaries) < MIN_POSTS:
            status, generated, gap = "few", None, None
        else:
            generated = median(salaries)
            gap = (generated - cell.median) / cell.median
            status = "ok" if abs(gap) <= TOLERANCE else "FLAG"
        rows.append({
            "role": cell.role,
            "bucket": cell.bucket,
            "n": len(salaries),
            "reference": cell.median,
            "generated": generated,
            "gap": gap,
            "status": status,
        })
    return rows


def main() -> None:
    data_dir = Path(sys.argv[1])
    truth = [
        json.loads(line)
        for line in (data_dir / "ground_truth.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    rows = check(truth, load_reference())
    print(f"{'role':16} {'bucket':7} {'n':>3} {'reference':>9} {'generated':>9} {'gap':>6}  status")
    for r in sorted(rows, key=lambda r: (r["role"], r["bucket"])):
        generated = f"{r['generated']:>9,.0f}" if r["generated"] else f"{'-':>9}"
        gap = f"{r['gap']:>+6.1%}" if r["gap"] is not None else f"{'-':>6}"
        print(f"{r['role']:16} {r['bucket']:7} {r['n']:>3} {r['reference']:>9,} {generated} {gap}  {r['status']}")
    flagged = [r for r in rows if r["status"] == "FLAG"]
    few = [r for r in rows if r["status"] == "few"]
    print(f"\n{len(rows)} cells: {len(flagged)} flagged (>{TOLERANCE:.0%}), {len(few)} with fewer than {MIN_POSTS} posts")


if __name__ == "__main__":
    main()
