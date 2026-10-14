import asyncio
import json
import sys
import time
from pathlib import Path

from app.agents.critic_agent import CriticVerdict, critique_candidate
from app.ingestion.review_loop import ReviewResult, extract_with_review
from app.tools.normalize_role import normalize_role
from app.tools.parse_amount import parse_amount
from evals.ablation_cases import CASES, Case

CONCURRENCY = 5
RESULTS_PATH = Path(__file__).parent / "results" / "ablation.json"


async def critic_always_agrees(raw_text, candidate) -> CriticVerdict:
    return CriticVerdict(agrees=True, issues=[])


def is_correct(case: Case, result: ReviewResult) -> bool:
    if not case.is_salary_post:
        return result.status == "rejected"
    c = result.candidate
    if c is None or not c.is_salary_post:
        return False
    expected = parse_amount(case.salary_text)
    return (
        c.role == normalize_role(case.role_text)
        and c.salary_min == expected.salary_min
        and c.salary_max == expected.salary_max
        and c.pay_basis == expected.pay_basis
        and bool(c.has_equity) == case.has_equity
    )


async def run_case(case: Case, critique, semaphore) -> dict:
    async with semaphore:
        started = time.perf_counter()
        result = await extract_with_review(case.post, critique=critique)
        return {
            "id": case.id,
            "category": case.category,
            "status": result.status,
            "rounds": result.rounds,
            "correct": is_correct(case, result),
            "seconds": round(time.perf_counter() - started, 2),
        }


def summarize(rows: list[dict]) -> dict:
    approved = [r for r in rows if r["status"] == "approved"]
    review = [r for r in rows if r["status"] == "needs_review"]
    wrong_in_review = [r for r in review if not r["correct"]]
    return {
        "cases": len(rows),
        "approved": len(approved),
        "approved_wrong": sum(1 for r in approved if not r["correct"]),
        "needs_review": len(review),
        "review_were_wrong": len(wrong_in_review),
        "review_false_alarms": len(review) - len(wrong_in_review),
        "rejected": sum(1 for r in rows if r["status"] == "rejected"),
        "total_wrong": sum(1 for r in rows if not r["correct"]),
        "avg_seconds": round(sum(r["seconds"] for r in rows) / len(rows), 2),
        "avg_rounds": round(sum(r["rounds"] for r in rows) / len(rows), 2),
    }


async def main() -> None:
    semaphore = asyncio.Semaphore(CONCURRENCY)
    conditions = {"with_critic": critique_candidate, "without_critic": critic_always_agrees}
    output = {}
    for name, critique in conditions.items():
        rows = await asyncio.gather(*(run_case(c, critique, semaphore) for c in CASES))
        output[name] = {"summary": summarize(rows), "rows": rows}
        print(name, json.dumps(output[name]["summary"], ensure_ascii=False))

    RESULTS_PATH.parent.mkdir(exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"saved {RESULTS_PATH}", file=sys.stderr)


if __name__ == "__main__":
    asyncio.run(main())
